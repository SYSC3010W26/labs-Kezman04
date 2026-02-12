#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import io
import threading

# CHANGE THIS TO YOUR NAME
HEADER_TEXT = "KZ - SYSC3010"

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output = StreamingOutput()

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            content = f"""
<html>
<head>
    <title>Pi Camera Stream</title>
</head>
<body>
    <h2>{HEADER_TEXT}</h2>
    <img src="/stream.mjpg" width="640" height="480" />
</body>
</html>
""".encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
            self.end_headers()

            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception:
                pass
        else:
            self.send_error(404)

def main():
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_video_configuration(main={"size": (640, 480)})
    )

    encoder = MJPEGEncoder(bitrate=2000000)
    picam2.start_recording(encoder, FileOutput(output))

    server = HTTPServer(("", 8000), StreamingHandler)
    print("Web stream running at http://<PI_IP>:8000")

    try:
        server.serve_forever()
    finally:
        picam2.stop_recording()

if __name__ == "__main__":
    main()
