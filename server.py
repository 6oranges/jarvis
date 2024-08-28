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
        json_data = json.dumps({"speak": speak,"keep_listening":keep_listening,"context":context})
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
                data = json.loads(post_data)
                commands = data["commands"]
            except:
                return self.illegal_request("Invalid JSON")
            if not isinstance(commands, list):
                return self.illegal_request("Unexpected structure")
            to_say = ""
            for command in commands:
                if not isinstance(command, str):
                    return self.illegal_request("Unexpected structure")
                command=command.lower()
                if not command.startswith("jarvis"):
                    continue
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
                elif "light" in command and "color" in command:
                    table = {
                        "white": (0, 0, 100),
                        "silver": (0, 0, 75),
                        "gray": (0, 0, 50),
                        "red": (0, 100, 100),
                        "maroon": (0, 100, 100),
                        "yellow": (60, 100, 100),
                        "olive": (60, 100, 50),
                        "lime": (120, 100, 100),
                        "green": (120, 100, 50),
                        "aqua": (180, 100, 100),
                        "teal": (180, 100, 50),
                        "blue": (240, 100, 100),
                        "navy": (240, 100, 50),
                        "fuchsia": (300, 100, 100),
                        "purple": (300, 100, 50),
                    }
                    for part in command.split():
                        if part in table:
                            h,s,v = table[part]
                            self.light_process.stdin.write(f"color {h} {s} {v}\n")
                            self.light_process.stdin.flush()
                            return self.say(speak="Changing color to " + part)
                    numbers = re.findall(r'\d+',command)
                    if len(numbers) == 3:
                        self.light_process.stdin.write(f"color {numbers[0]} {numbers[1]} {numbers[2]}\n")
                        self.light_process.stdin.flush()
                        return self.say(speak="Changing color to " + numbers[0] + " " + numbers[1] + " " + numbers[2])
                    return self.say("I don't know that color")
                else:
                    if to_say == "":
                        to_say = "Javis doesn't know how to"+command.replace("jarvis","")
            if to_say == "":
                return self.say()
            return self.say(speak=to_say)
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