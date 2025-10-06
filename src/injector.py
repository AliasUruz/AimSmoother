
import ctypes
from ctypes import wintypes

# Mapeamento de estruturas e constantes da API do Windows, conforme documentação da Microsoft.
# Estas definições permitem que o Python interaja com as funções de baixo nível do sistema operacional.

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

class MOUSEINPUT(ctypes.Structure):
    """
    Representa a estrutura MOUSEINPUT da WinAPI.
    Contém informações sobre um evento de mouse simulado.
    https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
    """
    _fields_ = [("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    """
    Representa a estrutura INPUT da WinAPI, uma união que pode conter
    informações sobre eventos de mouse, teclado ou hardware.
    https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
    """
    class _I(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    
    _anonymous_ = ("i",)
    _fields_ = [("type", wintypes.DWORD),
                ("i", _I)]

def send_mouse_move(dx: int, dy: int, magic_number: int):
    """
    Cria e envia um evento de movimento de mouse relativo para a fila de input do sistema.

    Args:
        dx: O movimento relativo no eixo X.
        dy: O movimento relativo no eixo Y.
        magic_number: Um número para marcar o evento como sintético, evitando loops de feedback.
    """
    extra = ctypes.c_ulong(magic_number)
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.i.mi = MOUSEINPUT(dx=dx, 
                          dy=dy, 
                          mouseData=0, 
                          dwFlags=MOUSEEVENTF_MOVE, 
                          time=0, 
                          dwExtraInfo=ctypes.pointer(extra))
    
    # A chamada para a API do Windows.
    # Envia 1 estrutura INPUT, cujo tamanho é especificado.
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
