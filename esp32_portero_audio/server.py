from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
PORT = 8099

class AudioHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            audio = self.rfile.read(length)

            print(f"[INFO] Recibidos {len(audio)} bytes de audio.")

            with open("/data/ultimo.raw", "ab") as f:
                f.write(audio)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            print("[ERROR]", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"ERROR")

    def log_message(self, *args):
        return  # Quita el spam

def main():
    print("Servidor escuchando en puerto", PORT)
    server = HTTPServer((HOST, PORT), AudioHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()

if __name__ == "__main__":
    main()
