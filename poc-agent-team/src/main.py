import http.server
import socketserver
import sys

def run():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at port {PORT}")
            httpd.serve_forever()
    except Exception:
        pass

if __name__ == "__main__":
    run()
