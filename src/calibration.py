from __future__ import annotations

import math
from typing import Optional

from .calibration_ui import CalibrationWindow
from .smoothing import AdaptiveEMA, LinearEMAParams
from .win_hook import HookEngine


class CalibrationCollector:
    """Armazena as amostras de velocidade por fase e gera recomendações."""

    def __init__(self) -> None:
        self._samples: dict[str, list[float]] = {"slow": [], "fast": []}

    def record(self, phase: str, dx: float, dy: float, dt: float) -> None:
        if dt <= 0:
            return
        speed = math.hypot(dx, dy) / dt
        self._samples.setdefault(phase, []).append(speed)

    def has_enough_data(self) -> bool:
        return all(len(values) >= 25 for values in self._samples.values())

    def recommendations(self, current: LinearEMAParams) -> Optional[LinearEMAParams]:
        if not self.has_enough_data():
            return None

        slow = sorted(self._samples.get("slow", []))
        fast = sorted(self._samples.get("fast", []))
        if not slow or not fast:
            return None

        v_min = percentile(slow, 0.65)
        v_med_fast = percentile(fast, 0.5)
        v_max = percentile(fast, 0.9)

        v_min = max(10.0, v_min * 0.75)
        v_max = max(v_min + 120.0, v_max * 1.1, v_med_fast * 1.3)

        return LinearEMAParams(
            v_min=float(round(v_min, 2)),
            v_max=float(round(v_max, 2)),
            alpha_min=float(round(current.alpha_min, 4)),
            alpha_max=float(round(current.alpha_max, 4)),
        )


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    fraction = min(1.0, max(0.0, fraction))
    index = int(round((len(values) - 1) * fraction))
    return values[index]


class CalibrationSession:
    """Orquestra o fluxo de calibração guiada."""

    def __init__(
        self,
        engine: HookEngine,
        ema: AdaptiveEMA,
        *,
        slow_duration_sec: float,
        fast_duration_sec: float,
    ) -> None:
        self.engine = engine
        self.ema = ema
        self.collector = CalibrationCollector()
        self.slow_duration = max(slow_duration_sec, 1.0)
        self.fast_duration = max(fast_duration_sec, 1.0)
        self.window = CalibrationWindow()
        self._closed = False

    def execute(self) -> None:
        """Executa o fluxo sincrono utilizando o mainloop do Tkinter."""
        self.window.on_close(self._handle_cancel)
        self.window.set_instruction("Bem-vindo! Vamos calibrar o AimSmoother.")
        self.window.set_status("A calibração dura cerca de 15 segundos e ajustará o filtro automaticamente.")
        self.window.after(1500, self._begin_slow_phase)
        self.window.mainloop()

    def _begin_slow_phase(self) -> None:
        if self._closed:
            return
        self.window.set_instruction("Fase LENTA: mova o mouse em círculos amplos, lentamente.")
        self.window.set_status("Mantemos apenas movimentos suaves; evite solavancos.")
        self._start_phase("slow", self.slow_duration)

    def _begin_fast_phase(self) -> None:
        if self._closed:
            return
        self.window.set_instruction("Fase RÁPIDA: mova o mouse mais rapidamente, como em um flick controlado.")
        self.window.set_status("Não precisa ser agressivo; o objetivo é capturar movimentos ágeis.")
        self._start_phase("fast", self.fast_duration)

    def _start_phase(self, phase: str, duration_sec: float) -> None:
        self.engine.start_calibration(phase, self.collector.record)
        self.window.run_progress(int(duration_sec * 1000))
        self.window.after(int(duration_sec * 1000), lambda: self._end_phase(phase))

    def _end_phase(self, phase: str) -> None:
        self.engine.stop_calibration()
        self.window.stop_progress()
        if phase == "slow":
            self.window.set_instruction("Ótimo! Agora prepare-se para a fase rápida.")
            self.window.set_status("A próxima etapa começa em 3 segundos.")
            self.window.after(3000, self._begin_fast_phase)
        else:
            self._finalize()

    def _finalize(self) -> None:
        self.window.set_instruction("Processando os dados coletados...")
        self.window.set_status("")
        self.window.after(600, self._apply_results)

    def _apply_results(self) -> None:
        suggestion = self.collector.recommendations(self.ema.params)
        if suggestion:
            self.ema.params.v_min = suggestion.v_min
            self.ema.params.v_max = suggestion.v_max
            self.ema.params.alpha_min = suggestion.alpha_min
            self.ema.params.alpha_max = suggestion.alpha_max
            summary = (
                f"Calibração concluída!\n"
                f"v_min={suggestion.v_min}, v_max={suggestion.v_max}\n"
                f"alpha_min={suggestion.alpha_min}, alpha_max={suggestion.alpha_max}"
            )
            self.window.set_instruction(summary)
            self.window.set_status("Os novos parâmetros já estão ativos. Clique em Fechar para continuar.")
        else:
            self.window.set_instruction("Calibração concluída, mas dados insuficientes para ajustes automáticos.")
            self.window.set_status("Tente novamente com movimentos mais contínuos.")
        self.window.after(3000, self._close_window)

    def _handle_cancel(self) -> None:
        self._closed = True
        self.engine.stop_calibration()
        self.window.stop_progress()
        self.window.destroy()

    def _close_window(self) -> None:
        if not self._closed:
            self._closed = True
            self.window.stop_progress()
            self.window.destroy()


def run_calibration(
    engine: HookEngine,
    ema: AdaptiveEMA,
    *,
    slow_duration_sec: float = 5.0,
    fast_duration_sec: float = 5.0,
) -> None:
    """
    Executa a calibração guiada. Quaisquer exceções do Tkinter são tratadas para
    não derrubar o aplicativo principal.
    """
    try:
        session = CalibrationSession(
            engine,
            ema,
            slow_duration_sec=slow_duration_sec,
            fast_duration_sec=fast_duration_sec,
        )
        session.execute()
    except Exception as exc:  # noqa: BLE001
        print(f"Calibração foi ignorada: {exc}")
