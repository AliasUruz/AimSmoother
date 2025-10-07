import ctypes
from ctypes import wintypes

if not hasattr(ctypes, "windll"):
    raise ImportError("hotkeys só pode ser utilizado no Windows (ctypes.windll indisponível).")

user32 = ctypes.windll.user32

MOD_NOREPEAT = 0x4000

VK_CODES = {
    "F10": 0x79,
    "F12": 0x7B,
}

VK_NAMES = {code: name for name, code in VK_CODES.items()}

ID_TOGGLE_HOTKEY = 1
ID_QUIT_HOTKEY = 2

RegisterHotKey = user32.RegisterHotKey
RegisterHotKey.argtypes = [wintypes.HWND, wintypes.INT, wintypes.UINT, wintypes.UINT]
RegisterHotKey.restype = wintypes.BOOL

UnregisterHotKey = user32.UnregisterHotKey
UnregisterHotKey.argtypes = [wintypes.HWND, wintypes.INT]
UnregisterHotKey.restype = wintypes.BOOL


class Hotkeys:
    def __init__(self, toggle_vk: str, quit_vk: str):
        if toggle_vk not in VK_CODES or quit_vk not in VK_CODES:
            raise ValueError("Hotkey não suportada.")

        self.toggle_vk = VK_CODES[toggle_vk]
        self.quit_vk = VK_CODES[quit_vk]
        self.hwnd = 0

    def register(self) -> None:
        if not RegisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY, MOD_NOREPEAT, self.toggle_vk):
            raise OSError(f"Falha ao registrar hotkey de toggle. Código Win32: {ctypes.get_last_error()}")
        if not RegisterHotKey(self.hwnd, ID_QUIT_HOTKEY, MOD_NOREPEAT, self.quit_vk):
            UnregisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY)
            raise OSError(f"Falha ao registrar hotkey de saída. Código Win32: {ctypes.get_last_error()}")
        print(
            "Hotkeys (ctypes) registradas: "
            f"Ligar/Desligar ({VK_NAMES[self.toggle_vk]}), "
            f"Sair ({VK_NAMES[self.quit_vk]})"
        )

    def unregister(self) -> None:
        UnregisterHotKey(self.hwnd, ID_TOGGLE_HOTKEY)
        UnregisterHotKey(self.hwnd, ID_QUIT_HOTKEY)
        print("Hotkeys desregistradas.")