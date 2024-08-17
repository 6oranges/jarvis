import http.server
import socketserver
import json
import re
import subprocess

PORT = 8000  # You can choose any port number

light_process = subprocess.Popen(['/home/tstander/python/bin/python', 'light.py'],stdin=subprocess.PIPE, text=True)

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if self.path == '/assist':
            print(f"POST data: {post_data}")
            try:
                commands = json.loads(post_data)
            except:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                # Sent no data
                self.wfile.write(b"")
                return
            if not isinstance(commands, list):
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Invalid request B")
                return
            for command in commands:
                command=command.lower()
                if not command.startswith("jarvis"):
                    continue
                if "light" in command and "turn" in command and "on" in command:
                    # Send a 200 OK response
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Turning on light")
                    #light_process.stdin.write("on\n")
                    #light_process.stdin.flush()
                    return
                elif "light" in command and "turn" in command and "off" in command:
                    # Send a 200 OK response
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Turning off light")
                    light_process.stdin.write("off\n")
                    light_process.stdin.flush()
                    return
                elif "light" in command and "brightness" in command:
                    # Send a 200 OK response
                    brightness = re.findall(r'\d+',command)[0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(bytes("Setting brightness to " + brightness + " percent","utf-8"))
                    light_process.stdin.write("brightness " + brightness + "\n")
                    light_process.stdin.flush()
                    return
            # Handle other paths with a 404 Not Found
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"")
        else:
            # Handle other paths with a 404 Not Found
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")

# Create the server
with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()