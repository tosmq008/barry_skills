#Requires -Version 5.1
<#
.SYNOPSIS
    adaptive-dev - 自适应持续开发守护脚本 v1.0 (PowerShell 版本)
    智能分析项目状态，动态调度多 Agent，持续迭代直到可用

.DESCRIPTION
    Windows PowerShell 版本的自适应持续开发引擎守护脚本

.EXAMPLE
    .\adaptive-dev.ps1 start "一个待办事项App"
    .\adaptive-dev.ps1 status
    .\adaptive-dev.ps1 stop
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'pause', 'status', 'logs', 'reset', 'help')]
    [string]$Command = 'help',

    [Parameter(Position = 1)]
    [string]$Requirement = ''
)

# ============================================
# 配置
# ============================================
$VERSION = "1.0.0"
$SCRIPT_NAME = "adaptive-dev"
$STATE_DIR = ".dev-state"
$MAX_TURNS = 50
$MIN_INTERVAL = 60
$MAX_INTERVAL = 120
$RATE_LIMIT_WAIT = 300
$MAX_ERRORS = 5
$SESSION_TIMEOUT = 1800
$HEARTBEAT_TIMEOUT = 1800
$CLAUDE_MODEL = if ($env:CLAUDE_MODEL) { $env:CLAUDE_MODEL } else { "claude-sonnet-4-20250514" }

# Skill 路径 (支持自定义)
$SKILL_DIR = if ($env:SKILL_DIR) { $env:SKILL_DIR } else { "$env:USERPROFILE\.claude\skills\adaptive-dev-engine" }

# 路径
$PROJECT_DIR = Get-Location
$STATE_FILE = Join-Path $PROJECT_DIR "$STATE_DIR\state.json"
$PID_FILE = Join-Path $PROJECT_DIR "$STATE_DIR\daemon.pid"
$LOG_DIR = Join-Path $PROJECT_DIR "$STATE_DIR\logs"
$REQUIREMENT_FILE = Join-Path $PROJECT_DIR "$STATE_DIR\requirement.txt"

# ============================================
# 工具函数
# ============================================

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Get-JsonValue {
    param([string]$Path)
    try {
        $state = Get-Content $STATE_FILE -Raw | ConvertFrom-Json
        $value = $state
        foreach ($key in $Path.Split('.')) {
            $value = $value.$key
        }
        return $value
    }
    catch {
        return $null
    }
}

function Set-JsonValue {
    param(
        [string]$Path,
        [object]$Value
    )
    try {
        $state = Get-Content $STATE_FILE -Raw | ConvertFrom-Json

        # 设置嵌套属性
        $keys = $Path.Split('.')
        $current = $state
        for ($i = 0; $i -lt $keys.Count - 1; $i++) {
            $current = $current.($keys[$i])
        }
        $current.($keys[-1]) = $Value

        # 更新心跳
        $state.last_heartbeat = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

        $state | ConvertTo-Json -Depth 10 | Set-Content $STATE_FILE -Encoding UTF8
    }
    catch {
        Write-Error "Failed to set JSON value: $_"
    }
}

function Get-ProjectState {
    # 返回: running | has_state | has_docs | empty

    # 1. 检查是否已在运行
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($pid) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                return "running"
            }
        }
    }

    # 2. 检查是否有状态文件
    if (Test-Path $STATE_FILE) {
        return "has_state"
    }

    # 3. 检查是否有项目文档
    if ((Test-Path "docs\prd") -and (Get-ChildItem "docs\prd\*.md" -ErrorAction SilentlyContinue)) {
        return "has_docs"
    }
    if ((Test-Path "PRD.md") -or (Test-Path "requirements.md") -or (Test-Path "README.md")) {
        return "has_docs"
    }

    # 4. 检查是否有代码目录 (常见项目结构)
    $codeDirs = @("src", "client", "admin", "app", "backend", "frontend", "server", "api", "lib", "packages", "modules")
    foreach ($dir in $codeDirs) {
        if (Test-Path $dir) {
            return "has_docs"
        }
    }

    # 5. 检查是否有项目配置文件 (各种语言/框架)
    $configFiles = @("package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json", "Makefile", "CMakeLists.txt")
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            return "has_docs"
        }
    }

    # 6. 检查是否有代码文件 (至少有一个)
    $codeExtensions = @("*.py", "*.js", "*.ts", "*.go", "*.rs", "*.java", "*.rb", "*.php", "*.c", "*.cpp", "*.h")
    foreach ($ext in $codeExtensions) {
        if (Get-ChildItem $ext -ErrorAction SilentlyContinue | Select-Object -First 1) {
            return "has_docs"
        }
    }

    return "empty"
}

# ============================================
# 命令实现
# ============================================

function Show-Help {
    @"
$SCRIPT_NAME v$VERSION - 自适应持续开发引擎 (PowerShell)

用法:
  .\adaptive-dev.ps1 start [需求描述]    启动持续开发
  .\adaptive-dev.ps1 stop                停止
  .\adaptive-dev.ps1 pause               暂停
  .\adaptive-dev.ps1 status              查看状态
  .\adaptive-dev.ps1 logs                实时日志
  .\adaptive-dev.ps1 reset               重置

自动判断逻辑:
  - 已在运行 → 提示已运行
  - 有状态文件 → 从断点继续
  - 有项目文档 → 基于现有项目继续
  - 空项目 → 需要传入需求描述

示例:
  # 空项目，从需求开始
  .\adaptive-dev.ps1 start "一个待办事项App，支持增删改查"

  # 已有项目或暂停后继续
  .\adaptive-dev.ps1 start

环境变量:
  CLAUDE_MODEL    使用的模型 (默认: claude-sonnet-4-20250514)
  SKILL_DIR       Skill 目录路径

"@
}

function Initialize-State {
    param(
        [string]$Name,
        [string]$RequirementText
    )

    # 创建目录
    $dirs = @("$STATE_DIR\logs", "$STATE_DIR\checkpoints", "$STATE_DIR\locks")
    foreach ($dir in $dirs) {
        $fullPath = Join-Path $PROJECT_DIR $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }

    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    # 保存需求
    if ($RequirementText) {
        $RequirementText | Set-Content $REQUIREMENT_FILE -Encoding UTF8
    }

    # 创建状态文件
    $state = @{
        version = $VERSION
        project = @{
            name = $Name
            path = $PROJECT_DIR.Path
            type = "unknown"
            created_at = $timestamp
        }
        health = @{
            score = 0
            breakdown = @{
                requirements = 0
                code = 0
                tests = 0
                runnable = 0
                quality = 0
            }
            usable = $false
            target = 80
            assessed_at = $null
            history = @()
        }
        status = "ready"
        exit_reason = $null
        current_action = $null
        agent_coordination = @{
            active_agents = @()
            completed_agents = @()
            pending_sync = $false
        }
        action_history = @()
        decision_log = @()
        blockers = @()
        errors = @()
        sessions = @{
            count = 0
            total_turns = 0
            current_session = $null
        }
        last_heartbeat = $timestamp
        metrics = @{
            total_duration_seconds = 0
            avg_health_delta_per_session = 0
            parallel_executions = 0
        }
    }

    $state | ConvertTo-Json -Depth 10 | Set-Content $STATE_FILE -Encoding UTF8
}

function Start-Daemon {
    param([string]$Name)

    Write-Host "🚀 启动自适应持续开发: $Name"
    Write-Host "   项目目录: $PROJECT_DIR"
    Write-Host "   模型: $CLAUDE_MODEL"

    # 启动后台作业
    $job = Start-Job -ScriptBlock {
        param($ProjectDir, $StateFile, $LogDir, $RequirementFile, $SkillDir, $ClaudeModel, $MaxTurns, $MinInterval, $MaxInterval, $SessionTimeout, $MaxErrors, $RateLimitWait)

        Set-Location $ProjectDir
        $logFile = Join-Path $LogDir "daemon.log"

        function Write-DaemonLog {
            param([string]$Message)
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$timestamp] $Message" | Add-Content $logFile
        }

        Write-DaemonLog "=========================================="
        Write-DaemonLog "守护进程启动 v1.0.0"
        Write-DaemonLog "模型: $ClaudeModel"
        Write-DaemonLog "=========================================="

        $errors = 0
        $rateLimitCount = 0

        while ($true) {
            if (-not (Test-Path $StateFile)) {
                Write-DaemonLog "ERROR: 状态文件丢失"
                Start-Sleep -Seconds 60
                continue
            }

            $state = Get-Content $StateFile -Raw | ConvertFrom-Json
            $status = $state.status
            $healthScore = $state.health.score

            Write-DaemonLog "当前状态: $status, 健康度: $healthScore"

            switch ($status) {
                { $_ -in @('ready', 'continue') } {
                    # 更新状态为 running
                    $state.status = 'running'
                    $state.sessions.count++
                    $state.last_heartbeat = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                    $state | ConvertTo-Json -Depth 10 | Set-Content $StateFile -Encoding UTF8

                    $sessionCount = $state.sessions.count
                    Write-DaemonLog "启动会话 #$sessionCount - 健康度: $healthScore"

                    # 读取需求
                    $requirement = ""
                    if (Test-Path $RequirementFile) {
                        $requirement = Get-Content $RequirementFile -Raw
                    }

                    # 构建 prompt
                    $prompt = @"
你正在自适应持续开发模式下工作。

## 工作规范
请先读取 skill 文档了解工作流程:
cat $SkillDir/SKILL.md

## 项目信息
- 项目名称: $($state.project.name)
- 项目目录: $ProjectDir
- 当前健康度: $healthScore/100
- 目标健康度: 80/100

## 执行步骤
1. 执行项目健康度分析（SKILL.md 中的 Step 1）
2. 计算健康度评分（Step 2）
3. 根据健康度智能决策下一步行动（Step 3）
4. 调度合适的 Agent 执行（Step 4）
5. 更新状态文件

## 备用需求描述（仅当项目完全为空时使用）
$requirement

## 重要规则
1. 每次会话先分析健康度
2. 优先使用并行调度提高效率
3. 健康度 >= 80 即可用，不要过度优化
4. 每完成一步更新 .dev-state/state.json
5. 接近轮次限制时保存断点退出

请开始执行。
"@

                    $sessionLog = Join-Path $LogDir "session-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
                    Write-DaemonLog "会话日志: $sessionLog"

                    $startTime = Get-Date

                    # 启动 claude
                    try {
                        $process = Start-Process -FilePath "claude" -ArgumentList "--print", "--dangerously-skip-permissions", "--max-turns", $MaxTurns, "--model", $ClaudeModel, "`"$prompt`"" -RedirectStandardOutput $sessionLog -RedirectStandardError "$sessionLog.err" -PassThru -NoNewWindow

                        # 等待完成或超时
                        $completed = $process.WaitForExit($SessionTimeout * 1000)

                        if (-not $completed) {
                            $process.Kill()
                            Write-DaemonLog "会话超时"
                        }

                        $exitCode = $process.ExitCode
                    }
                    catch {
                        Write-DaemonLog "会话错误: $_"
                        $exitCode = 1
                    }

                    $duration = ((Get-Date) - $startTime).TotalSeconds

                    if ($exitCode -eq 0) {
                        Write-DaemonLog "会话结束 (耗时: ${duration}s)"
                        $errors = 0
                        $rateLimitCount = 0
                    }
                    else {
                        Write-DaemonLog "会话退出 (code: $exitCode, 耗时: ${duration}s)"

                        # 检查限流
                        if (Test-Path $sessionLog) {
                            $logContent = Get-Content $sessionLog -Raw -ErrorAction SilentlyContinue
                            if ($logContent -match "rate.limit|429|too.many.requests") {
                                Write-DaemonLog "检测到限流"
                                $rateLimitCount++
                                $wait = [Math]::Min($RateLimitWait * $rateLimitCount, 1800)
                                Write-DaemonLog "限流等待 ${wait}s (第 $rateLimitCount 次)"
                                Start-Sleep -Seconds $wait
                                continue
                            }
                        }

                        $errors++
                        if ($errors -ge $MaxErrors) {
                            Write-DaemonLog "ERROR: 连续错误过多"
                            break
                        }
                    }

                    # 更新状态
                    $state = Get-Content $StateFile -Raw | ConvertFrom-Json
                    if ($state.status -eq 'running') {
                        $state.status = 'continue'
                        $state | ConvertTo-Json -Depth 10 | Set-Content $StateFile -Encoding UTF8
                    }

                    # 检查是否完成
                    if ($state.status -eq 'completed') {
                        Write-DaemonLog "🎉 项目达到可用状态！"
                        break
                    }

                    # 等待
                    $wait = Get-Random -Minimum $MinInterval -Maximum $MaxInterval
                    Write-DaemonLog "等待 ${wait}s"
                    Start-Sleep -Seconds $wait
                }

                'running' {
                    # 检查心跳超时
                    $lastHb = [DateTime]::Parse($state.last_heartbeat)
                    $age = ((Get-Date).ToUniversalTime() - $lastHb).TotalSeconds

                    if ($age -gt 1800) {
                        Write-DaemonLog "心跳超时，强制重启"
                        $state.status = 'continue'
                        $state.exit_reason = 'heartbeat_timeout'
                        $state | ConvertTo-Json -Depth 10 | Set-Content $StateFile -Encoding UTF8

                        # 尝试终止相关进程
                        Get-Process -Name "claude" -ErrorAction SilentlyContinue | Stop-Process -Force
                        Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
                        Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
                        Get-Process -Name "npm" -ErrorAction SilentlyContinue | Stop-Process -Force
                    }
                    Start-Sleep -Seconds 30
                }

                'paused' {
                    Write-DaemonLog "已暂停，等待恢复"
                    Start-Sleep -Seconds 60
                }

                'completed' {
                    Write-DaemonLog "🎉 项目完成！"
                    break
                }

                default {
                    Write-DaemonLog "未知状态: $status"
                    Start-Sleep -Seconds 30
                }
            }
        }
    } -ArgumentList $PROJECT_DIR.Path, $STATE_FILE, $LOG_DIR, $REQUIREMENT_FILE, $SKILL_DIR, $CLAUDE_MODEL, $MAX_TURNS, $MIN_INTERVAL, $MAX_INTERVAL, $SESSION_TIMEOUT, $MAX_ERRORS, $RATE_LIMIT_WAIT

    # 保存 Job ID
    $job.Id | Set-Content $PID_FILE

    Start-Sleep -Seconds 2

    if ($job.State -eq 'Running') {
        Write-Host ""
        Write-Host "✅ 已启动 (Job ID: $($job.Id))"
        Write-Host ""
        Write-Host "常用命令:"
        Write-Host "  .\adaptive-dev.ps1 status  查看状态"
        Write-Host "  .\adaptive-dev.ps1 logs    实时日志"
        Write-Host "  .\adaptive-dev.ps1 stop    停止"
    }
    else {
        Write-Host "❌ 启动失败"
        Receive-Job -Job $job
        exit 1
    }
}

function Invoke-Start {
    param([string]$RequirementText)

    # 检查依赖
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        if (-not (Get-Command "python3" -ErrorAction SilentlyContinue)) {
            Write-Host "❌ 需要 python"
            exit 1
        }
    }
    if (-not (Get-Command "claude" -ErrorAction SilentlyContinue)) {
        Write-Host "❌ 需要 claude CLI"
        exit 1
    }

    $projectName = Split-Path $PROJECT_DIR -Leaf
    $state = Get-ProjectState

    switch ($state) {
        'running' {
            $pid = Get-Content $PID_FILE
            Write-Host "⚠️  已在运行 (Job ID: $pid)"
            Write-Host "   使用 '.\adaptive-dev.ps1 status' 查看状态"
            Write-Host "   使用 '.\adaptive-dev.ps1 stop' 停止"
            exit 1
        }

        'has_state' {
            Write-Host "🔄 检测到断点，从上次继续..."
            $stateData = Get-Content $STATE_FILE -Raw | ConvertFrom-Json
            $projectName = $stateData.project.name

            if ($stateData.status -eq 'paused') {
                Write-Host "   (从暂停状态恢复)"
                Set-JsonValue -Path "status" -Value "continue"
            }

            Start-Daemon -Name $projectName
        }

        'has_docs' {
            Write-Host "📂 检测到现有项目，基于现有内容继续..."
            Initialize-State -Name $projectName -RequirementText ""
            Start-Daemon -Name $projectName
        }

        'empty' {
            if (-not $RequirementText) {
                Write-Host "❌ 空项目需要提供需求描述"
                Write-Host ""
                Write-Host "用法: .\adaptive-dev.ps1 start `"需求描述`""
                Write-Host ""
                Write-Host "示例:"
                Write-Host "  .\adaptive-dev.ps1 start `"一个待办事项App，支持创建、完成、删除任务`""
                exit 1
            }
            Write-Host "🆕 新项目，从需求开始..."
            Initialize-State -Name $projectName -RequirementText $RequirementText
            Start-Daemon -Name $projectName
        }
    }
}

function Invoke-Stop {
    if (-not (Test-Path $PID_FILE)) {
        Write-Host "⚠️  未运行"
        return
    }

    $jobId = Get-Content $PID_FILE
    $job = Get-Job -Id $jobId -ErrorAction SilentlyContinue

    if ($job) {
        Stop-Job -Job $job
        Remove-Job -Job $job
    }

    Remove-Item $PID_FILE -Force
    Write-Host "✅ 已停止"
}

function Invoke-Pause {
    if (-not (Test-Path $STATE_FILE)) {
        Write-Host "❌ 未初始化"
        exit 1
    }
    if (-not (Test-Path $PID_FILE)) {
        Write-Host "⚠️  未运行"
        return
    }

    Set-JsonValue -Path "status" -Value "paused"
    Set-JsonValue -Path "exit_reason" -Value "user_pause"

    Write-Host "⏸️  已暂停（完成当前会话后生效）"
    Write-Host "   使用 '.\adaptive-dev.ps1 start' 恢复"
}

function Show-Status {
    Write-Host "=========================================="
    Write-Host "📊 自适应持续开发状态"
    Write-Host "=========================================="

    $state = Get-ProjectState

    switch ($state) {
        'running' {
            $jobId = Get-Content $PID_FILE
            Write-Host "守护进程: ✅ 运行中 (Job ID: $jobId)"
        }
        'has_state' {
            Write-Host "守护进程: ⏹️  未运行 (有断点可继续)"
        }
        'has_docs' {
            Write-Host "守护进程: ⏹️  未运行 (检测到项目文档)"
        }
        'empty' {
            Write-Host "守护进程: ⏹️  未运行 (空项目)"
        }
    }

    if (-not (Test-Path $STATE_FILE)) {
        Write-Host ""
        Write-Host "使用 '.\adaptive-dev.ps1 start' 开始"
        return
    }

    $stateData = Get-Content $STATE_FILE -Raw | ConvertFrom-Json

    Write-Host ""
    Write-Host "项目: $($stateData.project.name)"
    Write-Host "状态: $($stateData.status)"

    $health = $stateData.health
    $usableText = if ($health.usable) { "✅ 可用" } else { "🔄 开发中" }
    Write-Host ""
    Write-Host "健康度: $($health.score)/100 $usableText"
    Write-Host "  需求: $($health.breakdown.requirements)/20"
    Write-Host "  代码: $($health.breakdown.code)/25"
    Write-Host "  测试: $($health.breakdown.tests)/20"
    Write-Host "  运行: $($health.breakdown.runnable)/20"
    Write-Host "  质量: $($health.breakdown.quality)/15"

    Write-Host ""
    Write-Host "会话: $($stateData.sessions.count) 次"

    if ($stateData.current_action) {
        Write-Host "当前行动: $($stateData.current_action.type)"
        if ($stateData.current_action.agents) {
            Write-Host "  Agent: $($stateData.current_action.agents -join ', ')"
        }
    }

    # 心跳
    if ($stateData.last_heartbeat) {
        try {
            $hbTime = [DateTime]::Parse($stateData.last_heartbeat)
            $age = [int]((Get-Date).ToUniversalTime() - $hbTime).TotalSeconds
            Write-Host ""
            Write-Host "心跳: ${age}s 前"
        }
        catch {}
    }

    # 错误
    if ($stateData.errors.Count -gt 0) {
        Write-Host ""
        Write-Host "错误: $($stateData.errors.Count) 个"
    }

    Write-Host ""
    Write-Host "最近日志:"
    $daemonLog = Join-Path $LOG_DIR "daemon.log"
    if (Test-Path $daemonLog) {
        Get-Content $daemonLog -Tail 5
    }
    else {
        Write-Host "  (无)"
    }
}

function Show-Logs {
    $daemonLog = Join-Path $LOG_DIR "daemon.log"
    if (-not (Test-Path $daemonLog)) {
        Write-Host "❌ 无日志"
        exit 1
    }
    Write-Host "📜 实时日志 (Ctrl+C 退出)"
    Get-Content $daemonLog -Wait -Tail 50
}

function Invoke-Reset {
    Invoke-Stop 2>$null
    $stateDir = Join-Path $PROJECT_DIR $STATE_DIR
    if (Test-Path $stateDir) {
        Remove-Item $stateDir -Recurse -Force
    }
    Write-Host "✅ 已重置"
}

# ============================================
# 入口
# ============================================

switch ($Command) {
    'start' { Invoke-Start -RequirementText $Requirement }
    'stop' { Invoke-Stop }
    'pause' { Invoke-Pause }
    'status' { Show-Status }
    'logs' { Show-Logs }
    'reset' { Invoke-Reset }
    'help' { Show-Help }
    default { Show-Help }
}
