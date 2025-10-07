from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class CalibrationWindow(tk.Tk):
    """Janela simples em Tkinter para guiar a calibração."""

    def __init__(self, title: str = "Assistente de Calibração AimSmoother"):
        super().__init__()
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._handle_close)

        self._on_close: Optional[Callable[[], None]] = None
        self._progress_job: str | None = None
        self._progress_start: float = 0.0
        self._progress_duration: float = 0.0

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        self.instruction = ttk.Label(container, text="", wraplength=360, justify="center")
        self.instruction.pack(fill="x", pady=(0, 16))

        self.progress = ttk.Progressbar(container, mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        self.status = ttk.Label(container, text="", wraplength=360, justify="center", foreground="#666666")
        self.status.pack(fill="x", pady=(16, 0))

    def set_instruction(self, message: str) -> None:
        self.instruction.config(text=message)
        self.update_idletasks()

    def set_status(self, message: str) -> None:
        self.status.config(text=message)
        self.update_idletasks()

    def run_progress(self, duration_ms: int) -> None:
        """Anima a barra de progresso por um determinado intervalo."""
        if self._progress_job is not None:
            self.after_cancel(self._progress_job)
            self._progress_job = None
        self._progress_start = time.perf_counter()
        self._progress_duration = max(duration_ms / 1000.0, 1e-3)
        self.progress["value"] = 0
        self._tick_progress()

    def stop_progress(self) -> None:
        if self._progress_job is not None:
            self.after_cancel(self._progress_job)
            self._progress_job = None
        self.progress["value"] = 0

    def on_close(self, callback: Callable[[], None]) -> None:
        self._on_close = callback

    def _tick_progress(self) -> None:
        elapsed = time.perf_counter() - self._progress_start
        percent = min(1.0, elapsed / self._progress_duration)
        self.progress["value"] = percent * 100
        if percent < 1.0:
            self._progress_job = self.after(33, self._tick_progress)
        else:
            self._progress_job = None

    def _handle_close(self) -> None:
        if self._on_close:
            self._on_close()
        else:
            self.stop_progress()
            self.destroy()
