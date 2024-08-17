import http.server
import socketserver
import asyncio
import json
from kasa import Discover

PORT = 8000  # You can choose any port number
ip_address = "192.168.1.213"
async def get_device():
    global ip_address
    device =  await Discover.discover_single(ip_address)
    if device is not None:
        print(f"Found device: {device}")
        return device
    devices = await Discover.discover()
    for key in devices:
        ip_address = key
        print(f"Found device: {device}")
        return devices[key]
async def turn_on_device():
    dev = await get_device()
    await dev.turn_on()
    await dev.update()
    print("Device turned on")

async def turn_off_device():
    dev = await get_device()
    await dev.turn_off()
    await dev.update()
    print("Device turned off")

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Start an asyncio event loop to handle async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if self.path == '/assist':
            print(f"POST data: {post_data}")
            try:
                commands = json.loads(post_data)
            except:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                # Sent no data
                self.wfile.write(b"")
                return
            if not isinstance(commands, list):
                self.send_response(400)
                self.send_header("Content-type", "text/html")
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
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Turning on light")
                    self.wfile.flush()
                    loop.run_until_complete(turn_on_device())
                    return
                elif "light" in command and "turn" in command and "off" in command:
                    # Send a 200 OK response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Turning off light")
                    self.wfile.flush()
                    loop.run_until_complete(turn_off_device())
                    return
            # Handle other paths with a 404 Not Found
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"")
        else:
            # Handle other paths with a 404 Not Found
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Not Found")
        
        loop.close()

# Create the server
with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()