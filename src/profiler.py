
import time

class LatencyProfiler:
    """
    Agrega dados de latência de processamento de eventos e os loga periodicamente.
    
    Esta abordagem evita a sobrecarga de I/O (chamadas a `print`) que ocorreria
    se logássemos cada evento individualmente, o que poderia mascarar ou até mesmo
    causar a latência que estamos tentando medir.
    """
    def __init__(self, log_interval_sec: float = 5.0):
        """
        Inicializa o profiler.

        Args:
            log_interval_sec: O intervalo em segundos entre cada log de média.
        """
        self.log_interval = log_interval_sec
        self.last_log_time = time.time()
        self.event_count = 0
        self.total_latency_us = 0

    def log(self, latency_us: float):
        """
        Registra uma única medição de latência em micro-segundos (µs).
        Acumula os valores e, se o intervalo de log for atingido, imprime a média.
        """
        self.event_count += 1
        self.total_latency_us += latency_us

        current_time = time.time()
        if current_time - self.last_log_time > self.log_interval:
            if self.event_count > 0:
                avg_latency = self.total_latency_us / self.event_count
                # O f-string formatado garante uma saída limpa e legível no console.
                print(f"[Profiler] Latência média de processamento nos últimos {self.log_interval:.1f}s: {avg_latency:.2f} µs ({self.event_count} eventos)")
            
            # Reseta as estatísticas para o próximo intervalo de medição.
            self.last_log_time = current_time
            self.event_count = 0
            self.total_latency_us = 0
