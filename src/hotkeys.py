import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

MOD_NOREPEAT = 0x4000

VK_CODES = {
    "F10": 0x79,
    "F12": 0x7B,
}

ID_TOGGLE_HOTKEY = 1
ID_QUIT_HOTKEY = 2

class Hotkeys:
    def __init__(self, toggle_vk: str, quit_vk: str):
        if toggle_vk not in VK_CODES or quit_vk not in VK_CODES:
            raise ValueError("Hotkey não suportada.")
        
        self.toggle_vk = VK_CODES[toggle_vk]
        self.quit_vk = VK_CODES[quit_vk]
        self.hwnd = 0

    def register(self) -> None:
        if not user32.RegisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY, MOD_NOREPEAT, self.toggle_vk):
            raise OSError()
        if not user32.RegisterHotKey(self.hwnd, ID_QUIT_HOTKEY, MOD_NOREPEAT, self.quit_vk):
            user32.UnregisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY)
            raise OSError()
        print(f"Hotkeys (ctypes) registradas: Ligar/Desligar ({list(VK_CODES.keys())[list(VK_CODES.values()).index(self.toggle_vk)]}), Sair ({list(VK_CODES.keys())[list(VK_CODES.values()).index(self.quit_vk)]})")

    def unregister(self) -> None:
        user32.UnregisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY)
        user32.UnregisterHotKey(self.hwnd, ID_QUIT_HOTKEY)
        print("Hotkeys desregistradas.")