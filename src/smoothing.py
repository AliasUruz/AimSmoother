
from dataclasses import dataclass
from math import hypot

@dataclass
class LinearEMAParams:
    """Armazena os parâmetros de configuração para o filtro EMA adaptativo."""
    v_min: float
    v_max: float
    alpha_min: float
    alpha_max: float

    def alpha_for_speed(self, v: float) -> float:
        """
        Calcula o fator de suavização 'alpha' dinamicamente com base na velocidade.
        Usa interpolação linear (lerp) entre alpha_min e alpha_max.
        """
        if self.v_max <= self.v_min:
            return self.alpha_max
        
        # Normaliza a velocidade para um fator t entre 0 e 1
        t = (v - self.v_min) / (self.v_max - self.v_min)
        
        # Garante que t permaneça no intervalo [0, 1] (clamp)
        t = max(0.0, min(1.0, t))
        
        # Interpolação linear
        return self.alpha_min + t * (self.alpha_max - self.alpha_min)

class AdaptiveEMA:
    """Implementa o filtro de Média Móvel Exponencial (EMA) adaptativo."""
    def __init__(self, params: LinearEMAParams):
        self.params = params
        self._sx = 0.0
        self._sy = 0.0
        self._initialized = False

    def update(self, dx: float, dy: float, dt: float, gain: float) -> tuple[float, float]:
        """
        Atualiza o filtro com um novo delta de movimento e retorna o delta suavizado.

        Args:
            dx: Delta de movimento bruto no eixo X.
            dy: Delta de movimento bruto no eixo Y.
            dt: Delta de tempo desde o último evento.
            gain: Fator de ganho (do TremorGuard) para amortecimento adicional.

        Returns:
            Uma tupla contendo o delta suavizado (dx, dy).
        """
        if not self._initialized:
            # No primeiro evento, não há histórico para suavizar. Apenas inicializa.
            self._sx, self._sy, self._initialized = dx, dy, True
            return dx, dy
        
        speed = hypot(dx, dy) / dt
        alpha = self.params.alpha_for_speed(speed)
        final_alpha = alpha * gain # Aplica o amortecimento extra do TremorGuard

        # Fórmula do filtro EMA aplicada a cada eixo independentemente.
        # O novo valor suavizado é uma média ponderada entre o input atual e o valor suavizado anterior.
        self._sx = (final_alpha * dx) + (1.0 - final_alpha) * self._sx
        self._sy = (final_alpha * dy) + (1.0 - final_alpha) * self._sy
        
        return self._sx, self._sy
