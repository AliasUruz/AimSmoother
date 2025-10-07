from __future__ import annotations

import ctypes
import time
from ctypes import wintypes, byref, cast, POINTER

from .smoothing import AdaptiveEMA
from .tremor import TremorGuard
from .profiler import LatencyProfiler
from . import injector

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200

LowLevelMouseProc = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.WPARAM, wintypes.LPARAM, ctypes.c_void_p)

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT),
                ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class HookEngine:
    def __init__(self, ema: AdaptiveEMA, tremor: TremorGuard, profiler: LatencyProfiler, magic_number: int):
        self.ema = ema
        self.tremor = tremor
        self.profiler = profiler
        self.magic_number = magic_number
        self._user_enabled = True
        self._pause_reasons: set[str] = set()
        self.mode = "smoothing"
        self._calibration_sink = None
        self.last_x = None
        self.last_y = None
        self.last_t = None
        self._hHook = None
        self.callback_ptr = LowLevelMouseProc(self._callback)

    @property
    def enabled(self) -> bool:
        """Retorna se o pipeline de suavização deve estar ativo."""
        return self._user_enabled and not self._pause_reasons and self.mode == "smoothing"

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._user_enabled = bool(value)

    def toggle_user_enabled(self) -> bool:
        """Inverte o estado solicitado pelo usuário."""
        self._user_enabled = not self._user_enabled
        return self.enabled

    def pause(self, reason: str) -> None:
        """Pausa o pipeline devido a uma condição externa (ex: jogo na blacklist)."""
        if reason not in self._pause_reasons:
            self._pause_reasons.add(reason)

    def resume(self, reason: str) -> None:
        """Remove a pausa aplicada por um motivo específico."""
        if reason in self._pause_reasons:
            self._pause_reasons.remove(reason)

    def start_calibration(self, phase: str, sink) -> None:
        """Configura o hook para coletar dados do mouse durante a calibração."""
        self.mode = f"calibration_{phase}"
        self._calibration_sink = sink
        self.last_x = None
        self.last_y = None
        self.last_t = None

    def stop_calibration(self) -> None:
        """Retorna o hook ao modo padrão de suavização."""
        self.mode = "smoothing"
        self._calibration_sink = None
        self.last_x = None
        self.last_y = None
        self.last_t = None

    def _callback(self, nCode, wParam, lParam):
        start_time = time.perf_counter_ns()
        try:
            hook_struct = cast(lParam, POINTER(MSLLHOOKSTRUCT)).contents
            if hook_struct.dwExtraInfo and hook_struct.dwExtraInfo.contents.value == self.magic_number:
                return user32.CallNextHookEx(self._hHook, nCode, wParam, lParam)
            if wParam == WM_MOUSEMOVE:
                current_x = hook_struct.pt.x
                current_y = hook_struct.pt.y
                current_t = time.perf_counter()
                if self.last_x is None:
                    self.last_x, self.last_y, self.last_t = current_x, current_y, current_t
                    return user32.CallNextHookEx(self._hHook, nCode, wParam, lParam)
                dx = current_x - self.last_x
                dy = current_y - self.last_y
                dt = current_t - self.last_t
                if dt > 0:
                    if self.mode.startswith("calibration") and self._calibration_sink:
                        phase = self.mode.split("_", 1)[1]
                        self._calibration_sink(phase, dx, dy, dt)
                        self.last_x, self.last_y, self.last_t = current_x, current_y, current_t
                        return user32.CallNextHookEx(self._hHook, nCode, wParam, lParam)

                    if self.enabled:
                        processed_dx, processed_dy, gain = self.tremor.preprocess(dx, dy, dt)
                        smoothed_dx, smoothed_dy = self.ema.update(processed_dx, processed_dy, dt, gain)
                        if smoothed_dx != 0 or smoothed_dy != 0:
                            injector.send_mouse_move(int(round(smoothed_dx)), int(round(smoothed_dy)), self.magic_number)
                self.last_x, self.last_y, self.last_t = current_x, current_y, current_t
                if self.enabled:
                    end_time = time.perf_counter_ns()
                    self.profiler.log((end_time - start_time) / 1000.0)
                    return 1
        except Exception as e:
            print(f"Erro no callback do hook: {e}")
        return user32.CallNextHookEx(self._hHook, nCode, wParam, lParam)

    def install(self):
        # A CORREÇÃO DEFINITIVA: Usar o handle da user32.dll para ancorar o hook.
        h_module = kernel32.GetModuleHandleW("user32.dll")
        self._hHook = user32.SetWindowsHookExA(WH_MOUSE_LL, self.callback_ptr, h_module, 0)
        if not self._hHook:
            raise OSError(f"Falha ao instalar o hook. Código de erro: {ctypes.get_last_error()}")
        print("Hook de mouse (ctypes) instalado com sucesso.")

    def uninstall(self):
        if self._hHook:
            user32.UnhookWindowsHookEx(self._hHook)
            self._hHook = None
            print("Hook de mouse desinstalado.")
