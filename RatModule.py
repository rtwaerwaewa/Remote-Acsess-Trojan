import importlib
import subprocess
import sys

class Modules_class:
    def __init__(self, *modules):
        self.module_list = list(modules)

    def install_and_import_control(self, importing: bool = True) -> None:
        for module in self.module_list:
            try:
                importlib.import_module(module)
                print(f"'{module}' zaten yüklü.")
            except ImportError:
                print(f"'{module}' yüklü değil, yükleniyor...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"'{module}' başarıyla yüklendi.")

if __name__ == '__main__':
    module = Modules_class("vidstream", "socket", "requests")
    module.install_and_import_control()