#Requires -Version 5.1
<#
.SYNOPSIS
    adaptive-dev - 自适应持续开发守护脚本 v2.0 (PowerShell 版本)
    v2.0: 独立健康度评估、完整上下文传递、文件锁、进程隔离、git集成

.EXAMPLE
    .\adaptive-dev.ps1 start "一个待办事项App"
    .\adaptive-dev.ps1 status
    .\adaptive-dev.ps1 health
    .\adaptive-dev.ps1 feedback "修复登录页面"
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = 'help',

    [Parameter(Position = 1)]
    [string]$Argument = ''
)

# ============================================
# 加载配置 (项目级 > skill级 > 默认值)
# ============================================
$VERSION = "2.0.0"
$SCRIPT_NAME = "adaptive-dev"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$SCRIPT_PATH = $MyInvocation.MyCommand.Path
$PROJECT_DIR = if ($Command -eq '_daemon' -and $Argument) { $Argument } else { (Get-Location).Path }

function Import-ConfigEnv {
    param([string]$FilePath)
    $result = @{}
    if (-not (Test-Path $FilePath)) { return $result }
    Get-Content $FilePath | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#') -and $line -match '^([A-Z_]+)=(.*)$') {
            $outerKey = $Matches[1]
            $val = $Matches[2].Trim('"').Trim("'")
            if ($val -match '^\$\{([^:]+):-([^}]+)\}$') {
                $envVal = [Environment]::GetEnvironmentVariable($Matches[1])
                $val = if ($envVal) { $envVal } else { $Matches[2] }
            }
            $result[$outerKey] = $val
        }
    }
    return $result
}

$cfg = Import-ConfigEnv (Join-Path $SCRIPT_DIR "config.env")
$projCfg = Import-ConfigEnv (Join-Path (Join-Path $PROJECT_DIR ".dev-state") "config.env")
foreach ($k in $projCfg.Keys) { $cfg[$k] = $projCfg[$k] }

function CfgVal { param([string]$Key, [string]$Default) if ($cfg[$Key]) { $cfg[$Key] } else { $Default } }

# Cross-platform Python detection
$script:PY = if (Get-Command "python3" -ErrorAction SilentlyContinue) { "python3" }
             elseif (Get-Command "python" -ErrorAction SilentlyContinue) { "python" }
             else { $null }

$STATE_DIR          = CfgVal 'STATE_DIR' '.dev-state'
$MAX_TURNS          = [int](CfgVal 'MAX_TURNS' '40')
$MIN_INTERVAL       = [int](CfgVal 'MIN_INTERVAL' '60')
$MAX_INTERVAL       = [int](CfgVal 'MAX_INTERVAL' '120')
$RATE_LIMIT_WAIT    = [int](CfgVal 'RATE_LIMIT_WAIT' '300')
$RATE_LIMIT_BACKOFF = [double](CfgVal 'RATE_LIMIT_BACKOFF' '1.5')
$MAX_ERRORS         = [int](CfgVal 'MAX_ERRORS' '5')
$SESSION_TIMEOUT    = [int](CfgVal 'SESSION_TIMEOUT' '1800')
$HEARTBEAT_TIMEOUT  = [int](CfgVal 'HEARTBEAT_TIMEOUT' '900')
$CLAUDE_MODEL       = if ($env:CLAUDE_MODEL) { $env:CLAUDE_MODEL } else { CfgVal 'CLAUDE_MODEL' 'claude-sonnet-4-20250514' }
$SKILL_DIR          = if ($env:SKILL_DIR) { $env:SKILL_DIR } else { CfgVal 'SKILL_DIR' (Join-Path $HOME ".claude/skills/adaptive-dev-engine") }
$GIT_AUTO_COMMIT    = CfgVal 'GIT_AUTO_COMMIT' 'true'
$GIT_ROLLBACK       = CfgVal 'GIT_ROLLBACK_ON_FAILURE' 'false'
$MAX_TOTAL_SESSIONS = [int](CfgVal 'MAX_TOTAL_SESSIONS' '100')
$LOG_RETENTION_DAYS = [int](CfgVal 'LOG_RETENTION_DAYS' '7')
$MAX_LOG_FILES      = [int](CfgVal 'MAX_LOG_FILES' '50')
$ALERT_WEBHOOK      = CfgVal 'ALERT_WEBHOOK' ''

# Paths
$STATE_FILE      = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "state.json"
$PID_FILE        = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "daemon.pid"
$LOG_DIR         = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "logs"
$CHECKPOINT_DIR  = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "checkpoints"
$REQUIREMENT_FILE = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "requirement.txt"
$HEALTH_CHECK    = Join-Path $SCRIPT_DIR "health-check.py"

# ============================================
# 工具函数
# ============================================

function Write-Log {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] $Msg"
}

function Get-Json {
    param([string]$Expr)
    $script:PY -c "import json; print(json.load(open(r'$STATE_FILE'))$Expr)" 2>$null
}

function Set-Json {
    param([string]$Stmts)
    $script:PY -c @"
import json, os
from datetime import datetime, timezone
sf = r'$STATE_FILE'
try:
    import msvcrt
    with open(sf, 'r+', encoding='utf-8') as f:
        sz = max(os.path.getsize(sf), 1)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, sz)
        try:
            d = json.load(f)
            $Stmts
            d['last_heartbeat'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            f.seek(0); f.truncate()
            json.dump(d, f, indent=2, ensure_ascii=False)
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, sz)
except ImportError:
    import fcntl
    with open(sf, 'r+', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            d = json.load(f)
            $Stmts
            d['last_heartbeat'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            f.seek(0); f.truncate()
            json.dump(d, f, indent=2, ensure_ascii=False)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
"@ 2>$null
}

function Send-Alert {
    param([string]$Level, [string]$Msg)
    Write-Log "ALERT [$Level]: $Msg"
    if ($ALERT_WEBHOOK) {
        try {
            $body = @{ text = "[$Level] adaptive-dev: $Msg" } | ConvertTo-Json
            Invoke-RestMethod -Uri $ALERT_WEBHOOK -Method Post -Body $body -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
        } catch {}
    }
}

function Remove-OldLogs {
    $cutoff = (Get-Date).AddDays(-$LOG_RETENTION_DAYS)
    Get-ChildItem (Join-Path $LOG_DIR "session-*.log") -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem (Join-Path $CHECKPOINT_DIR "checkpoint-*.json") -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force -ErrorAction SilentlyContinue
    $logs = Get-ChildItem (Join-Path $LOG_DIR "session-*.log") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if ($logs -and $logs.Count -gt $MAX_LOG_FILES) {
        $logs | Select-Object -Skip $MAX_LOG_FILES | Remove-Item -Force -ErrorAction SilentlyContinue
    }
    # Also clean .err files
    Get-ChildItem (Join-Path $LOG_DIR "session-*.log.err") -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force -ErrorAction SilentlyContinue
}

function Save-Checkpoint {
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item $STATE_FILE "$CHECKPOINT_DIR/checkpoint-$ts.json" -ErrorAction SilentlyContinue
    Copy-Item $STATE_FILE "$CHECKPOINT_DIR/latest.json" -ErrorAction SilentlyContinue
}

function Invoke-GitAutoCommit {
    if ($GIT_AUTO_COMMIT -ne "true" -or -not (Test-Path (Join-Path $PROJECT_DIR ".git"))) { return }
    Push-Location $PROJECT_DIR
    try {
        $n = Get-Json "['sessions']['count']"; if (-not $n) { $n = 0 }
        git add -A -- ':!.dev-state' 2>$null
        git diff --cached --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            git commit -m "auto: pre-session-${n} checkpoint" --no-verify 2>$null | Out-Null
        }
    } finally { Pop-Location }
}

function Invoke-GitRollback {
    if ($GIT_ROLLBACK -ne "true" -or -not (Test-Path (Join-Path $PROJECT_DIR ".git"))) { return }
    Push-Location $PROJECT_DIR
    try {
        $msg = git log -1 --format="%s" 2>$null
        if ($msg -and $msg.StartsWith("auto:")) {
            git revert HEAD --no-edit --no-verify 2>$null | Out-Null
        }
    } finally { Pop-Location }
}


# ============================================
# 错误分类与智能恢复
# ============================================

function Classify-Exit {
    param([string]$LogFile, [int]$ExitCode, [int]$Duration)
    if (-not (Test-Path $LogFile)) { return "unknown_crash" }

    # Session timeout (duration-based, check first as most reliable signal)
    if ($Duration -ge $SESSION_TIMEOUT) { return "session_timeout" }

    $lc = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
    if (-not $lc) { return "unknown_crash" }

    if ($lc -match "context.*window|context.*token.*limit|conversation.*too.*long|maximum.*context|context.*length|max.*tokens") { return "context_exhausted" }
    if ($lc -match "rate.limit|HTTP.*429|status.*429|too.many.requests") { return "rate_limit" }
    if ($lc -match "ECONNREFUSED|ECONNRESET|ETIMEDOUT|network.*error|connection.*refused|connection.*reset|fetch.*failed") { return "network_error" }
    if ($lc -match "permission.*denied|EACCES|unauthorized|HTTP.*401|status.*401|403.*forbidden|invalid.*api.*key") { return "permission_error" }
    if ($lc -match "tool.*execution.*failed|command.*not.*found|spawn.*ENOENT") { return "tool_error" }

    return "unknown_crash"
}

function Get-LastErrorContext {
    param([string]$LogFile)
    if (-not (Test-Path $LogFile)) { return "" }
    $lines = Select-String -Path $LogFile -Pattern "error|fail|exception|traceback|panic" -AllMatches -ErrorAction SilentlyContinue |
        Select-Object -Last 5 | ForEach-Object { $_.Line }
    return ($lines -join "`n")
}

function Get-ProjectState {
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($pid) {
            $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($p -and -not $p.HasExited) { return "running" }
        }
    }
    if (Test-Path $STATE_FILE) { return "has_state" }
    if ((Test-Path "docs/prd") -and (Get-ChildItem "docs/prd/*.md" -ErrorAction SilentlyContinue)) { return "has_docs" }
    foreach ($f in @("PRD.md", "requirements.md", "README.md")) { if (Test-Path $f) { return "has_docs" } }
    foreach ($d in @("src","client","admin","app","backend","frontend","server","api","lib","packages")) { if (Test-Path $d) { return "has_docs" } }
    foreach ($f in @("package.json","pyproject.toml","requirements.txt","Cargo.toml","go.mod","pom.xml","Makefile")) { if (Test-Path $f) { return "has_docs" } }
    return "empty"
}

# ============================================
# 初始化 & 启动
# ============================================

function Initialize-State {
    param([string]$Name, [string]$Req)
    foreach ($d in @("logs","checkpoints","agents")) {
        $p = Join-Path $PROJECT_DIR (Join-Path $STATE_DIR $d)
        if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    }
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    if ($Req) { $Req | Set-Content $REQUIREMENT_FILE -Encoding UTF8 }
    # Escape project name and path for JSON safety
    $safeName = $Name -replace '\\','\\\\' -replace '"','\"' -replace "`r",'' -replace "`n",' '
    $safePath = $PROJECT_DIR -replace '\\','\\\\' -replace '"','\"'
    @"
{
  "version": "$VERSION",
  "project": {"name": "$safeName", "path": "$safePath", "type": "unknown", "created_at": "$ts"},
  "health": {"score": 0, "breakdown": {"requirements": 0, "code": 0, "tests": 0, "runnable": 0, "quality": 0}, "details": {}, "usable": false, "target": 80, "assessed_at": null, "history": [], "delta": 0},
  "status": "ready", "exit_reason": null, "current_action": null,
  "agent_coordination": {"active_agents": [], "completed_agents": [], "pending_sync": false},
  "action_history": [], "decision_log": [], "blockers": [], "errors": [],
  "sessions": {"count": 0, "total_turns": 0, "current_session": null},
  "last_heartbeat": "$ts",
  "metrics": {"total_duration_seconds": 0, "parallel_executions": 0, "avg_health_delta_per_session": 0}
}
"@ | Set-Content $STATE_FILE -Encoding UTF8
    if (Test-Path $HEALTH_CHECK) { $script:PY $HEALTH_CHECK --project-dir $PROJECT_DIR --update 2>$null }
}

function Start-Daemon {
    param([string]$Name)
    Write-Host "启动自适应持续开发: $Name"
    Write-Host "  项目: $PROJECT_DIR"
    Write-Host "  模型: $CLAUDE_MODEL"

    # Ensure required directories exist (may be missing in resume path)
    foreach ($d in @("logs","checkpoints","agents")) {
        $p = Join-Path $PROJECT_DIR (Join-Path $STATE_DIR $d)
        if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    }

    # Re-invoke this script with _daemon command as a real process (fixes Job ID vs PID issue)
    # Cross-platform: use pwsh on all platforms
    $shell = if ($PSVersionTable.PSEdition -eq "Core") { "pwsh" } else { "powershell.exe" }
    $proc = Start-Process -FilePath $shell `
        -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $SCRIPT_PATH, "_daemon", $PROJECT_DIR `
        -WindowStyle Hidden -PassThru

    $proc.Id | Set-Content $PID_FILE
    Start-Sleep -Seconds 2

    if (-not $proc.HasExited) {
        Write-Host ""
        Write-Host "已启动 (PID: $($proc.Id))"
        Write-Host "  .\adaptive-dev.ps1 status    查看状态"
        Write-Host "  .\adaptive-dev.ps1 logs      实时日志"
        Write-Host "  .\adaptive-dev.ps1 stop      停止"
        Write-Host "  .\adaptive-dev.ps1 health    健康度检查"
        Write-Host "  .\adaptive-dev.ps1 feedback `"内容`"  写入反馈"
    }
    else {
        Write-Host "启动失败"
        $dl = Join-Path $LOG_DIR "daemon.log"
        if (Test-Path $dl) { Get-Content $dl -Tail 5 }
        exit 1
    }
}

# ============================================
# 守护进程 (via _daemon command)
# ============================================

function Run-Session {
    $script:sessionResult = 1
    $sessionCount = [int](Get-Json "['sessions']['count']" 2>$null)

    # Pre-session health check
    Write-Log "Pre-session health check..." | Add-Content "$LOG_DIR/daemon.log"
    $healthScore = 0
    if (Test-Path $HEALTH_CHECK) {
        $hj = $script:PY $HEALTH_CHECK --project-dir $PROJECT_DIR --update --json 2>$null
        try { $healthScore = [int]($hj | $script:PY -c "import sys,json; print(json.load(sys.stdin)['score'])" 2>$null) } catch {}
    }
    if (-not $healthScore) { $healthScore = [int](Get-Json "['health']['score']" 2>$null) }

    if ($healthScore -ge 80) {
        Write-Log "Health $healthScore >= 80, project usable!" | Add-Content "$LOG_DIR/daemon.log"
        Set-Json "d['status']='completed'; d['exit_reason']='usable_reached'"
        $script:sessionResult = 0; return
    }

    Write-Log "启动会话 #$($sessionCount + 1) - 健康度: $healthScore" | Add-Content "$LOG_DIR/daemon.log"
    Invoke-GitAutoCommit
    Set-Json "d['status']='running'; d['sessions']['count']=d['sessions'].get('count',0)+1"

    $requirement = ""; if (Test-Path $REQUIREMENT_FILE) { $requirement = Get-Content $REQUIREMENT_FILE -Raw }
    $userFeedback = ""; $fbFile = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "user-feedback.md"
    if (Test-Path $fbFile) { $userFeedback = Get-Content $fbFile -Raw }

    # Build context from state
    $contextInfo = $script:PY -c @"
import json
try:
    with open(r'$STATE_FILE') as f:
        s = json.load(f)
    parts = []
    ca = s.get('current_action') or {}
    cp = ca.get('checkpoint')
    if cp:
        parts.append('## Checkpoint (resume from here)')
        parts.append(f"- Step: {cp.get('step','N/A')}")
        parts.append(f"- Progress: {cp.get('progress','N/A')}")
        parts.append(f"- Next: {cp.get('next_action','N/A')}")
        if cp.get('context'): parts.append(f"- Context: {cp['context']}")
    h = s.get('health',{}); bd = h.get('breakdown',{}); det = h.get('details',{})
    mx = {'requirements':20,'code':25,'tests':20,'runnable':20,'quality':15}
    parts.append(f"\n## Health Breakdown ({h.get('score',0)}/100)")
    for dim in mx:
        parts.append(f"- {dim}: {bd.get(dim,0)}/{mx[dim]} ({det.get(dim,'')})")
    if bd:
        ratios = {k: bd.get(k,0)/mx[k] for k in mx}
        w = min(ratios, key=ratios.get)
        parts.append(f"\n**Weakest dimension: {w} ({bd.get(w,0)}/{mx[w]})**")
    ah = s.get('action_history',[])
    if ah:
        parts.append('\n## Recent Actions')
        for a in ah[-5:]: parts.append(f"- [{a.get('completed_at','?')}] {a.get('type','?')}: {a.get('result','?')}")
    bl = s.get('blockers',[])
    if bl:
        parts.append(f"\n## Blockers ({len(bl)})")
        for b in bl[-3:]: parts.append(f"- {b}")
    er = s.get('errors',[])
    if er:
        parts.append('\n## Recent Errors')
        for e in er[-3:]: parts.append(f"- [{e.get('timestamp','?')}] {e.get('message',e.get('type','?'))}")
    print('\n'.join(parts))
except Exception as e:
    print(f'(Context error: {e})')
"@ 2>$null

    # Get previous error context for prompt
    $prevErrors = $script:PY -c @"
import json
try:
    with open(r'$STATE_FILE') as f:
        s = json.load(f)
    errs = s.get('errors', [])
    if errs:
        last = errs[-1]
        print(f"Last error: [{last.get('type','?')}] {last.get('message','')}")
        t = last.get('type','')
        if t == 'context_exhausted': print('Recovery: Context was exhausted. Work efficiently, use /compact if needed.')
        elif t == 'tool_error': print('Recovery: A tool failed. Try alternative approach or skip.')
        elif t == 'network_error': print('Recovery: Network issue. Should be resolved now.')
    else:
        print('(none)')
except Exception:
    print('(none)')
"@ 2>$null

    $tc = $MAX_TURNS - 5
    $pn = Get-Json "['project']['name']"
    $prompt = "You are in adaptive continuous development mode.`n`n## Skill Documentation`nRead the skill doc first: cat $SKILL_DIR/SKILL.md`n`n## Project Info`n- Name: $pn`n- Directory: $PROJECT_DIR`n- Health: $healthScore/100 (assessed by independent script, DO NOT re-score)`n- Target: 80/100`n- Session: #$($sessionCount + 1)`n- Max turns: $MAX_TURNS (save checkpoint by turn $tc)`n`n## Session Context`n$contextInfo`n`n## Previous Errors`n$prevErrors`n`n## Requirement (for empty projects only)`n$requirement"
    if ($userFeedback) { $prompt += "`n`n## User Feedback (IMPORTANT - address this)`n$userFeedback" }
    $prompt += "`n`n## Rules`n1. Health is ALREADY computed - trust the score above, focus on weakest dimension`n2. Read SKILL.md for decision rules and Agent dispatch`n3. Update .dev-state/state.json after each major step`n4. Save checkpoint by turn $tc and exit gracefully`n5. Do NOT use pkill for cleanup`n6. If context gets long (many tool calls), use /compact to free space before running out`n7. If a tool/command fails repeatedly (3+ times), record as blocker and move on`n8. Before exiting, always ensure checkpoint is saved for next session recovery`n`nBegin."

    $sessionLog = "$LOG_DIR/session-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $startTime = Get-Date
    Write-Log "Session log: $sessionLog" | Add-Content "$LOG_DIR/daemon.log"

    # Write prompt to temp file to avoid Start-Process argument escaping issues
    $promptFile = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "session-prompt.txt"
    $prompt | Set-Content $promptFile -Encoding UTF8

    try {
        # Use shell wrapper to pipe prompt file to claude (avoids multi-line argument corruption)
        $shell = if ($PSVersionTable.PSEdition -eq "Core") { "pwsh" } else { "powershell.exe" }
        $runScript = "Get-Content -Raw '$promptFile' | & claude --print --dangerously-skip-permissions --max-turns $MAX_TURNS --model '$CLAUDE_MODEL'"
        $proc = Start-Process -FilePath $shell `
            -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$runScript `
            -RedirectStandardOutput $sessionLog -RedirectStandardError "$sessionLog.err" `
            -PassThru -WindowStyle Hidden
        $proc.Id | Set-Content (Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "claude.pid") -ErrorAction SilentlyContinue
        $completed = $proc.WaitForExit($SESSION_TIMEOUT * 1000)
        if (-not $completed) {
            $proc.Kill()
            $proc.WaitForExit(5000)
            Write-Log "会话超时" | Add-Content "$LOG_DIR/daemon.log"
            Set-Json "d['status']='continue'; d['exit_reason']='session_timeout'"
        }
        $exitCode = if ($proc.HasExited) { $proc.ExitCode } else { 1 }
    }
    catch {
        Write-Log "会话错误: $_" | Add-Content "$LOG_DIR/daemon.log"
        $exitCode = 1
    }
    Remove-Item (Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "claude.pid") -Force -ErrorAction SilentlyContinue

    $duration = [int]((Get-Date) - $startTime).TotalSeconds

    # Post-session health check
    Write-Log "Post-session health check..." | Add-Content "$LOG_DIR/daemon.log"
    if (Test-Path $HEALTH_CHECK) { $script:PY $HEALTH_CHECK --project-dir $PROJECT_DIR --update 2>$null }
    $newHealth = Get-Json "['health']['score']"

    if ($exitCode -eq 0) {
        Write-Log "会话结束 (${duration}s) 健康度: $healthScore -> $newHealth" | Add-Content "$LOG_DIR/daemon.log"
        $cs = Get-Json "['status']"
        if ($cs -eq "running") { Set-Json "d['status']='continue'" }
        $script:sessionResult = 0; return
    }

    # Classify exit reason
    $errorType = Classify-Exit -LogFile $sessionLog -ExitCode $exitCode -Duration $duration
    $errorCtx = (Get-LastErrorContext -LogFile $sessionLog) -replace "'", " " -replace '"', " "
    if ($errorCtx.Length -gt 200) { $errorCtx = $errorCtx.Substring(0, 200) }
    Write-Log "会话退出 (code: $exitCode, ${duration}s, type: $errorType) 健康度: $healthScore -> $newHealth" | Add-Content "$LOG_DIR/daemon.log"

    # Record error in state
    $safeCtx = $errorCtx -replace "`n", " " -replace "`r", " " -replace '[\\]', ' ' -replace "'", " " -replace '\$', ' '
    Set-Json "d['status']='continue'; d['exit_reason']='$errorType'; d.setdefault('errors',[]).append({'type':'$errorType','timestamp':d['last_heartbeat'],'message':'$safeCtx'.strip(),'session':d['sessions'].get('count',0)}); d['errors']=d['errors'][-10:]"

    switch ($errorType) {
        "rate_limit"        { Write-Log "检测到限流" | Add-Content "$LOG_DIR/daemon.log"; $script:sessionResult = 2; return }
        "context_exhausted" { Write-Log "上下文耗尽，下次会话将以新上下文重启" | Add-Content "$LOG_DIR/daemon.log"; $script:sessionResult = 3; return }
        "network_error"     { Write-Log "网络错误，短暂等待后重试" | Add-Content "$LOG_DIR/daemon.log"; $script:sessionResult = 4; return }
        "permission_error"  { Write-Log "权限错误，需要人工介入" | Add-Content "$LOG_DIR/daemon.log"; Send-Alert "ERROR" "权限错误"; $script:sessionResult = 5; return }
        "session_timeout"   { Write-Log "会话超时，自动重启" | Add-Content "$LOG_DIR/daemon.log"; $script:sessionResult = 6; return }
        default             { $script:sessionResult = 99; return }
    }
}

function Start-DaemonLoop {
    $daemonLog = "$LOG_DIR/daemon.log"
    Write-Log "==========================================" | Add-Content $daemonLog
    Write-Log "守护进程启动 v$VERSION" | Add-Content $daemonLog
    Write-Log "模型: $CLAUDE_MODEL | 最大轮次: $MAX_TURNS" | Add-Content $daemonLog
    Write-Log "==========================================" | Add-Content $daemonLog

    $errors = 0; $rlCount = 0; $loop = 0
    $shouldExit = $false

    while (-not $shouldExit) {
        $loop++
        if ($loop % 50 -eq 0) { Remove-OldLogs }
        if (-not (Test-Path $STATE_FILE)) {
            Write-Log "ERROR: 状态文件丢失" | Add-Content $daemonLog; Start-Sleep 60; continue
        }

        $status = Get-Json "['status']"
        # Detect corrupted state.json (Get-Json returns $null)
        if (-not $status) {
            $cpLatest = Join-Path $CHECKPOINT_DIR "latest.json"
            if (Test-Path $cpLatest) {
                Write-Log "WARN: state.json 损坏，从 checkpoint 恢复" | Add-Content $daemonLog
                Copy-Item $cpLatest $STATE_FILE -Force
                $status = Get-Json "['status']"
            }
            if (-not $status) {
                Write-Log "ERROR: state.json 损坏且无法恢复" | Add-Content $daemonLog
                Send-Alert "ERROR" "state.json 损坏"; $shouldExit = $true; continue
            }
        }
        $hs = 0; try { $hs = [int](Get-Json "['health']['score']") } catch { $hs = 0 }
        $ts = 0; try { $ts = [int](Get-Json "['sessions']['count']") } catch { $ts = 0 }
        Write-Log "状态: $status | 健康度: $hs | 会话: $ts" | Add-Content $daemonLog

        if ($MAX_TOTAL_SESSIONS -gt 0 -and $ts -ge $MAX_TOTAL_SESSIONS) {
            Write-Log "达到最大会话数 ($MAX_TOTAL_SESSIONS)，停止" | Add-Content $daemonLog
            Send-Alert "WARN" "达到最大会话数限制"; $shouldExit = $true; return
        }

        switch ($status) {
            { $_ -in @('ready','continue') } {
                $er = Get-Json "['exit_reason']"
                if ($er -eq "rate_limit") {
                    $w = [int][Math]::Min($RATE_LIMIT_WAIT * [Math]::Pow($RATE_LIMIT_BACKOFF, $rlCount), 1800)
                    $rlCount++
                    Write-Log "限流等待 ${w}s (第 $rlCount 次)" | Add-Content $daemonLog
                    Start-Sleep $w
                }
                Save-Checkpoint
                Run-Session
                $ret = $script:sessionResult
                switch ($ret) {
                    0 { $errors = 0; $rlCount = 0 }
                    2 { continue }  # Rate limit
                    3 { Write-Log "上下文恢复: 新会话将自动获得新上下文" | Add-Content $daemonLog }
                    4 { Write-Log "网络恢复: 等待 30s 后重试" | Add-Content $daemonLog; Start-Sleep 30 }
                    5 {
                        $errors++
                        if ($errors -ge $MAX_ERRORS) {
                            Write-Log "ERROR: 权限错误过多，需要人工介入" | Add-Content $daemonLog
                            Send-Alert "ERROR" "权限错误过多，已停止"; $shouldExit = $true; return
                        }
                    }
                    6 { Write-Log "会话超时恢复: 自动重启" | Add-Content $daemonLog }
                    default {
                        $errors++
                        if ($errors -ge $MAX_ERRORS) {
                            Write-Log "ERROR: 连续错误过多 ($errors)" | Add-Content $daemonLog
                            Send-Alert "ERROR" "连续错误过多"; $shouldExit = $true; return
                        }
                        Invoke-GitRollback
                    }
                }

                $ns = Get-Json "['status']"
                if ($ns -eq "completed") {
                    Write-Log "项目达到可用状态!" | Add-Content $daemonLog
                    Send-Alert "INFO" "项目完成! 健康度: $(Get-Json "['health']['score']")"; $shouldExit = $true; return
                }
                $w = Get-Random -Minimum $MIN_INTERVAL -Maximum ($MAX_INTERVAL + 1)
                Write-Log "等待 ${w}s" | Add-Content $daemonLog; Start-Sleep $w
            }
            'running' {
                $lhb = Get-Json "['last_heartbeat']"
                if ($lhb) {
                    try {
                        $age = [int]((Get-Date).ToUniversalTime() - [DateTime]::Parse($lhb)).TotalSeconds
                        if ($age -gt $HEARTBEAT_TIMEOUT) {
                            Write-Log "心跳超时 (${age}s)" | Add-Content $daemonLog
                            Set-Json "d['status']='continue'; d['exit_reason']='heartbeat_timeout'"
                            # Kill stale claude process
                            $cpf = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "claude.pid"
                            if (Test-Path $cpf) {
                                $cpid = Get-Content $cpf -ErrorAction SilentlyContinue
                                if ($cpid) {
                                    # Kill child processes first (process tree)
                                    if ($IsWindows -or (-not $IsLinux -and -not $IsMacOS)) {
                                        Get-CimInstance Win32_Process -Filter "ParentProcessId=$cpid" -ErrorAction SilentlyContinue |
                                            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
                                    } elseif ($IsLinux -or $IsMacOS) {
                                        & pkill -P $cpid 2>$null
                                    }
                                    Stop-Process -Id $cpid -Force -ErrorAction SilentlyContinue
                                }
                                Remove-Item $cpf -Force -ErrorAction SilentlyContinue
                            }
                            Start-Sleep 5
                        }
                    } catch {}
                }
                Start-Sleep 30
            }
            'paused' { Write-Log "已暂停" | Add-Content $daemonLog; Start-Sleep 60 }
            'completed' { Write-Log "项目完成!" | Add-Content $daemonLog; $shouldExit = $true; return }
            default { Write-Log "未知状态: $status" | Add-Content $daemonLog; Start-Sleep 30 }
        }
    }
}

# ============================================
# 命令
# ============================================

function Invoke-Start {
    param([string]$Req)
    if (-not $script:PY) { Write-Host "需要 python3 或 python"; exit 1 }
    if (-not (Get-Command "claude" -ErrorAction SilentlyContinue)) { Write-Host "需要 claude CLI"; exit 1 }

    $pn = Split-Path $PROJECT_DIR -Leaf
    $state = Get-ProjectState

    switch ($state) {
        'running' {
            Write-Host "已在运行 (PID: $(Get-Content $PID_FILE))"
            Write-Host "  .\adaptive-dev.ps1 status  查看状态"
            Write-Host "  .\adaptive-dev.ps1 stop    停止"
            exit 1
        }
        'has_state' {
            Write-Host "检测到断点，从上次继续..."
            $pn = Get-Json "['project']['name']"; if (-not $pn) { $pn = Split-Path $PROJECT_DIR -Leaf }
            $cs = Get-Json "['status']"
            if ($cs -eq "paused") { Set-Json "d['status']='continue'" }
            Start-Daemon -Name $pn
        }
        'has_docs' {
            Write-Host "检测到现有项目，基于现有内容继续..."
            Initialize-State -Name $pn -Req ""
            Start-Daemon -Name $pn
        }
        'empty' {
            if (-not $Req) {
                Write-Host "空项目需要提供需求描述"
                Write-Host "用法: .\adaptive-dev.ps1 start `"需求描述`""
                exit 1
            }
            Write-Host "新项目，从需求开始..."
            Initialize-State -Name $pn -Req $Req
            Start-Daemon -Name $pn
        }
    }
}

function Invoke-Stop {
    if (-not (Test-Path $PID_FILE)) { Write-Host "未运行"; return }
    # Save checkpoint and set status before killing
    if (Test-Path $STATE_FILE) {
        Save-Checkpoint
        Set-Json "d['status']='paused'; d['exit_reason']='user_stop'"
    }
    # Kill claude process if running
    $cpf = Join-Path (Join-Path $PROJECT_DIR $STATE_DIR) "claude.pid"
    if (Test-Path $cpf) {
        $cpid = Get-Content $cpf -ErrorAction SilentlyContinue
        if ($cpid) {
            Stop-Process -Id $cpid -Force -ErrorAction SilentlyContinue
            Start-Sleep 1
        }
        Remove-Item $cpf -Force -ErrorAction SilentlyContinue
    }
    # Kill daemon process
    $pid = Get-Content $PID_FILE
    try {
        $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($p -and -not $p.HasExited) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep 2
            $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($p -and -not $p.HasExited) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
        }
    } catch {}
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    Write-Host "已停止"
}

function Invoke-Pause {
    if (-not (Test-Path $STATE_FILE)) { Write-Host "未初始化"; exit 1 }
    if (-not (Test-Path $PID_FILE)) { Write-Host "未运行"; return }
    Set-Json "d['status']='paused'; d['exit_reason']='user_pause'"
    Write-Host "已暂停（完成当前会话后生效）"
    Write-Host "  .\adaptive-dev.ps1 start 恢复"
}

function Invoke-Health {
    if (Test-Path $HEALTH_CHECK) { $script:PY $HEALTH_CHECK --project-dir $PROJECT_DIR }
    else { Write-Host "health-check.py not found at $HEALTH_CHECK"; exit 1 }
}

function Invoke-Feedback {
    param([string]$Text)
    if (-not $Text) { Write-Host "用法: .\adaptive-dev.ps1 feedback `"反馈内容`""; exit 1 }
    $sd = Join-Path $PROJECT_DIR $STATE_DIR
    if (-not (Test-Path $sd)) { New-Item -ItemType Directory -Path $sd -Force | Out-Null }
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "${ts}: $Text" | Add-Content (Join-Path $sd "user-feedback.md") -Encoding UTF8
    Write-Host "反馈已记录，下次会话将读取"
}

function Show-Status {
    Write-Host "=========================================="
    Write-Host "自适应持续开发状态"
    Write-Host "=========================================="
    $state = Get-ProjectState
    switch ($state) {
        'running'   { Write-Host "守护进程: 运行中 (PID: $(Get-Content $PID_FILE))" }
        'has_state' { Write-Host "守护进程: 未运行 (有断点)" }
        'has_docs'  { Write-Host "守护进程: 未运行 (有项目)" }
        'empty'     { Write-Host "守护进程: 未运行 (空项目)" }
    }
    if (-not (Test-Path $STATE_FILE)) { Write-Host ""; Write-Host ".\adaptive-dev.ps1 start 开始"; return }
    if (Test-Path $HEALTH_CHECK) { Write-Host ""; $script:PY $HEALTH_CHECK --project-dir $PROJECT_DIR }
    Write-Host ""
    $script:PY -c @"
import json
with open(r'$STATE_FILE') as f:
    s = json.load(f)
print(f"项目: {s['project']['name']}")
print(f"状态: {s['status']}")
print(f"会话: {s['sessions'].get('count', 0)} 次")
ca = s.get('current_action')
if ca: print(f"当前: {ca.get('type', 'N/A')}")
ah = s.get('action_history', [])
if ah:
    last = ah[-1]
    print(f"上次: {last.get('type', '?')} -> {last.get('result', '?')}")
if s.get('errors'): print(f"错误: {len(s['errors'])} 个")
if s.get('blockers'): print(f"阻塞: {len(s['blockers'])} 个")
"@
    Write-Host ""; Write-Host "最近日志:"
    $dl = Join-Path $LOG_DIR "daemon.log"
    if (Test-Path $dl) { Get-Content $dl -Tail 5 } else { Write-Host "  (无)" }
}

function Show-Logs {
    $dl = Join-Path $LOG_DIR "daemon.log"
    if (-not (Test-Path $dl)) { Write-Host "无日志"; exit 1 }
    Write-Host "实时日志 (Ctrl+C 退出)"
    Get-Content $dl -Wait -Tail 50
}

function Show-Help {
    @"
$SCRIPT_NAME v$VERSION - 自适应持续开发引擎 (PowerShell)

用法:
  .\adaptive-dev.ps1 start [需求描述]    启动持续开发
  .\adaptive-dev.ps1 stop                停止
  .\adaptive-dev.ps1 pause               暂停
  .\adaptive-dev.ps1 status              查看状态
  .\adaptive-dev.ps1 logs                实时日志
  .\adaptive-dev.ps1 health              运行健康度检查
  .\adaptive-dev.ps1 feedback "内容"     写入反馈
  .\adaptive-dev.ps1 reset               重置

示例:
  .\adaptive-dev.ps1 start "一个待办事项App，支持增删改查"
  .\adaptive-dev.ps1 start
  .\adaptive-dev.ps1 health
  .\adaptive-dev.ps1 feedback "请优先修复登录功能"

环境变量:
  CLAUDE_MODEL    使用的模型 (默认: claude-sonnet-4-20250514)
  SKILL_DIR       Skill 目录路径
"@
}

function Invoke-Reset {
    Invoke-Stop 2>$null
    $sd = Join-Path $PROJECT_DIR $STATE_DIR
    if (Test-Path $sd) { Remove-Item $sd -Recurse -Force }
    Write-Host "已重置"
}

# ============================================
# 入口
# ============================================

switch ($Command) {
    'start'    { Invoke-Start -Req $Argument }
    'stop'     { Invoke-Stop }
    'pause'    { Invoke-Pause }
    'status'   { Show-Status }
    'logs'     { Show-Logs }
    'health'   { Invoke-Health }
    'feedback' { Invoke-Feedback -Text $Argument }
    'reset'    { Invoke-Reset }
    '_daemon'  { if (-not $script:PY) { Write-Host 'ERROR: python3/python not found'; exit 1 }; if (-not (Get-Command 'claude' -ErrorAction SilentlyContinue)) { Write-Host 'ERROR: claude CLI not found'; exit 1 }; Start-DaemonLoop }
    'help'     { Show-Help }
    default    { Show-Help }
}
