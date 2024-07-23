import http.server
import socketserver
import threading
import json
from urllib.parse import urlparse, parse_qs
import os
import socket
import datetime

PORT = 3000

SOCKET_PORT = 5000

WEB_DIR = r"C:\Users\User\Desktop\projects\Python_WEB\python-web-module-4\front-init"

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/":
            self.path = "/index.html"
        elif parsed_path.path == "/message":
            self.path = "/message.html"
        elif self.path.startswith("/static/"):
            pass
        else:
            self.path = "/error.html"
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))

            message = {
                "username": data.get('username', [''])[0],
                "message": data.get('message', [''])[0]
            }

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(json.dumps(message).encode('utf-8'), ('localhost', SOCKET_PORT))
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404)

def run_http_server():
    os.chdir(WEB_DIR)
    handler = MyHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving HTTP on port {PORT}")
    httpd.serve_forever()

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        message = json.loads(data.decode('utf-8'))
        timestamp = str(datetime.datetime.now())

        if not os.path.exists('storage'):
            os.makedirs('storage')

        if os.path.exists('storage/data.json'):
            with open('storage/data.json', 'r') as file:
                messages = json.load(file)
        else:
            messages = {}

        messages[timestamp] = message

        with open('storage/data.json', 'w') as file:
            json.dump(messages, file, indent=4)

def run_socket_server():
    server = socketserver.UDPServer(('localhost', SOCKET_PORT), MyUDPHandler)
    print(f"Serving Socket on port {SOCKET_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)

    http_thread.start()
    socket_thread.start()

    http_thread.join()
    socket_thread.join()
