
import ctypes
from ctypes import wintypes

if not hasattr(ctypes, "windll"):
    raise ImportError("injector só pode ser utilizado no Windows (ctypes.windll indisponível).")

# Mapeamento de estruturas e constantes da API do Windows, conforme documentação da Microsoft.
# Estas definições permitem que o Python interaja com as funções de baixo nível do sistema operacional.

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001


class MOUSEINPUT(ctypes.Structure):
    """Representa a estrutura MOUSEINPUT da WinAPI."""

    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    """Representa a estrutura INPUT da WinAPI."""

    class _I(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("i",)
    _fields_ = [("type", wintypes.DWORD), ("i", _I)]


SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = wintypes.UINT


def send_mouse_move(dx: int, dy: int, magic_number: int) -> None:
    """Envia um evento de movimento relativo do mouse."""

    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.i.mi = MOUSEINPUT(
        dx=dx,
        dy=dy,
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE,
        time=0,
        dwExtraInfo=magic_number,
    )

    inserted = SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    if inserted != 1:
        raise OSError(f"SendInput falhou. Código Win32: {ctypes.get_last_error()}")
