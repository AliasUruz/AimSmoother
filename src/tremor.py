
from dataclasses import dataclass
from math import hypot

@dataclass
class TremorParams:
    """Armazena os parâmetros de configuração para o filtro de tremor."""
    jitter_deadzone_px: float
    jitter_speed_max: float
    extra_damp_factor: float

class TremorGuard:
    """
    Implementa um pré-filtro para combater o tremor do mouse (jitter).
    Atua de duas formas: uma deadzone para ruído de baixa amplitude e um
    amortecimento extra para movimentos intencionais de velocidade muito baixa.
    """
    def __init__(self, p: TremorParams):
        self.p = p

    def preprocess(self, dx: float, dy: float, dt: float) -> tuple[float, float, float]:
        """
        Aplica a lógica de deadzone e amortecimento extra.

        Returns:
            Uma tupla (dx, dy, gain) onde dx/dy são os deltas pré-processados
            e 'gain' é um fator de multiplicação para o alpha do filtro EMA.
        """
        if dt <= 0:
            return dx, dy, 1.0

        speed = hypot(dx, dy) / dt
        
        # 1. Lógica de Deadzone: Se o movimento for lento E de baixa amplitude,
        # considera-se ruído e é zerado.
        if speed < self.p.jitter_speed_max and hypot(dx, dy) < self.p.jitter_deadzone_px:
            dx, dy = 0.0, 0.0
        
        # 2. Lógica de Amortecimento Extra: Se o movimento for extremamente lento,
        # retorna um fator de ganho < 1.0. Isso tornará o filtro EMA principal
        # ainda mais forte, aumentando a suavização.
        gain_extra = 1.0
        if speed < 50.0: # Este valor (50.0) pode ser futuramente parametrizado
            gain_extra = 1.0 - self.p.extra_damp_factor
            
        return dx, dy, gain_extra
