import http.server
import socketserver
import json
import re
import subprocess

PORT = 8000  # You can choose any port number


class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    light_process = subprocess.Popen(['/home/tstander/python/bin/python', 'light.py'],stdin=subprocess.PIPE, text=True)
    def say(self, speak="", keep_listening=False,context={}):
        self.send_response(200)
        json_data = json.dumps({"speak": speak,"await":keep_listening,"context":context})
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_data, "utf-8"))
    def illegal_request(self,reason):
        self.send_response(400)
        json_data = json.dumps({"error": reason})
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_data, "utf-8"))
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if self.path == '/assist':
            print(f"POST data: {post_data}")
            try:
                commands = json.loads(post_data)
            except:
                return self.illegal_request("Invalid JSON")
            if not isinstance(commands, list):
                return self.illegal_request("Unexpected structure")
            jarvis=False
            for command in commands:
                command=command.lower()
                if not command.startswith("jarvis"):
                    continue
                jarvis=True
                if "light" in command and "turn" in command and "on" in command:
                    self.light_process.stdin.write("on\n")
                    self.light_process.stdin.flush()
                    return self.say(speak="Turning on light")
                elif "light" in command and "turn" in command and "off" in command:
                    self.light_process.stdin.write("off\n")
                    self.light_process.stdin.flush()
                    return self.say(speak="Turning off light")
                elif "light" in command and "brightness" in command:
                    # Send a 200 OK response
                    numbers = re.findall(r'\d+',command)
                    if len(numbers) == 0:
                        return self.say()
                    brightness = numbers[0]
                    self.light_process.stdin.write("brightness " + brightness + "\n")
                    self.light_process.stdin.flush()
                    return self.say(speak="Setting brightness to " + brightness + " percent")
            if not jarvis:
                return self.say()
            return self.say(speak="Javis doesn't know how to "+command[0])
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