from kiteconnect import KiteConnect
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import threading
import time

# Zerodha API credentials
api_key = "8qq6ag2yl1bb582t"
api_secret = "odxrjws6dyxxa8hl0nqpdtvkmqz0tfx7"
redirect_port = 8000

kite = KiteConnect(api_key=api_key)
request_token_holder = {}

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(parsed_path.query)
        request_token = query.get("request_token", [None])[0]

        if request_token:
            request_token_holder["token"] = request_token
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<h1>✅ Login successful! You can close this window.</h1>".encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("❌ Request token not found.".encode('utf-8'))

def run_server():
    server = HTTPServer(("127.0.0.1", redirect_port), TokenHandler)
    print(f"🚀 Waiting for login at http://127.0.0.1:{redirect_port} ...")
    server.handle_request()

# Step 1: Start the local server
thread = threading.Thread(target=run_server)
thread.start()

# Step 2: Open the Zerodha login URL
print("🔗 Opening Zerodha login URL. Please log in:")
print(kite.login_url())

# Step 3: Wait up to 5 seconds for login
thread.join(timeout=5)

# Step 4: Check if request token was received
request_token = request_token_holder.get("token")
if not request_token:
    print("❌ Failed to get request_token in 5 seconds. Exiting.")
    exit()

# Step 5: Generate access token
try:
    session = kite.generate_session(request_token, api_secret=api_secret)
    access_token = session["access_token"]
    kite.set_access_token(access_token)

    with open("access_token.txt", "w") as f:
        f.write(access_token)

    print("✅ Access token saved:", access_token)

except Exception as e:
    print("❌ Error generating access token:", e)
