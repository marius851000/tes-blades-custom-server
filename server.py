# mostly vibe-coded main file that format stuff nicely for MainSession

import json
import urllib.parse
import http.server
import socketserver

from dispatch import MainSession, Request

PORT = 8000

MAIN_SESSION = MainSession()

class MultiHandler(http.server.BaseHTTPRequestHandler):
    """BaseHTTPRequestHandler that forwards every request to a common handler."""

    # --------------------------------------------------------------------- GET
    def do_GET(self):
        self._handle_request()

    # --------------------------------------------------------------------- POST
    def do_POST(self):
        self._handle_request()

    # --------------------------------------------------------------------- PUT
    def do_PUT(self):
        self._handle_request()

    # ------------------------------------------------------------------- PATCH
    def do_PATCH(self):
        self._handle_request()

    # ------------------------------------------------------------------ DELETE
    def do_DELETE(self):
        self._handle_request()

    # ----------------------------------------------------------------- OPTIONS
    def do_OPTIONS(self):
        self._handle_request()

    # --------------------------------------------------------------------- HEAD
    def do_HEAD(self):
        self._handle_request()

    # ------------------------------------------------------------------ TRACE
    def do_TRACE(self):
        self._handle_request()

    # ------------------------------------------------------------------- common
    def _handle_request(self):
        """Process the request and send a JSON response."""
        # 1. Parse URL
        parsed = urllib.parse.urlparse(self.path)
        full_path_and_query = parsed.path + ('?' + parsed.query if parsed.query else '')
        if full_path_and_query.startswith("/"):
            full_path_and_query = full_path_and_query[1:]

        # 2. Read body only if the method expects one
        body = None
        if self.command in ("POST", "PUT", "PATCH"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)



        #TODO: headers if they ever become usefull
        request = Request(full_path_and_query, body, {}, self.command)
        response = MAIN_SESSION.process_request(request)

        # 4. Send headers & body

        self.send_response(response.status)
        self.send_header("Content-Length", str(len(response.body)))
        for header_key in response.headers:
            self.send_header(header_key, response.headers[header_key])
        self.end_headers()

        # HEAD requests should not return a body
        if self.command != "HEAD":
            self.wfile.write(response.body)

    # --------------------------------------------------------------------- log
    def log_message(self, format, *args):
        """Silence the default STDOUT logging for cleaner demo output."""
        pass


# ------------------------------------------------------------------------ main
if __name__ == "__main__":
    # Tell the OS we’re okay with re‑binding the same port while it’s in
    # TIME_WAIT.  Must be set before the constructor binds the socket.
    class ReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = ReuseTCPServer(("", PORT), MultiHandler)
    try:
        print(f"Running on http://localhost:{PORT}")
        server.serve_forever()
    finally:
        print("\nShutting down cleanly…")
        server.shutdown()          # stops serve_forever loop
        server.server_close()      # releases the socket
        print("shut down finished?")
