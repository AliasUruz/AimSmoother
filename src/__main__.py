import ctypes
import json
import sys
import threading
import time
from pathlib import Path
from ctypes import wintypes, byref

# Importa todos os nossos módulos
from .smoothing import AdaptiveEMA, LinearEMAParams
from .tremor import TremorGuard, TremorParams
from .win_hook import HookEngine
from .hotkeys import Hotkeys, ID_TOGGLE_HOTKEY, ID_QUIT_HOTKEY
from .profiler import LatencyProfiler
from .calibration import run_calibration

# Constante para a mensagem de hotkey do Windows
WM_HOTKEY = 0x0312

def monitor_foreground_process(engine, blacklist, stop_event, gui, proc, psutil_mod, *, poll_interval: float = 0.5):
    """Observa o processo em foco e pausa/resume a suavização conforme a blacklist."""
    normalized = {item.lower() for item in blacklist}
    blocked_active = False
    while not stop_event.wait(poll_interval):
        try:
            hwnd = gui.GetForegroundWindow()
            if not hwnd:
                continue
            _, pid = proc.GetWindowThreadProcessId(hwnd)
            if not pid:
                continue
            name = psutil_mod.Process(pid).name().lower()
        except psutil_mod.NoSuchProcess:
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"Monitor de processos encontrou um erro: {exc}")
            time.sleep(1.0)
            continue

        if name in normalized and not blocked_active:
            blocked_active = True
            engine.pause("blacklist")
            print(f"Processo '{name}' está na blacklist. Suavização pausada automaticamente.")
        elif name not in normalized and blocked_active:
            blocked_active = False
            engine.resume("blacklist")
            status = "ATIVADO" if engine.enabled else "DESATIVADO"
            print(f"Processo liberado. Suavização: {status}.")

def load_cfg() -> dict:
    """Carrega o arquivo de configuração JSON."""
    try:
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "defaults.json"
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo de configuração 'defaults.json' não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Erro: Arquivo de configuração 'defaults.json' está mal formatado.")
        sys.exit(1)

def main():
    """Ponto de entrada principal do aplicativo."""
    print("Iniciando o Suavizador de Mira (usando ctypes)...")
    cfg = load_cfg()

    # 1. Instancia todos os componentes com os parâmetros do arquivo de configuração
    ema_params = LinearEMAParams(v_min=cfg["v_min"], v_max=cfg["v_max"], alpha_min=cfg["alpha_min"], alpha_max=cfg["alpha_max"])
    tremor_params = TremorParams(jitter_deadzone_px=cfg["jitter_deadzone_px"], jitter_speed_max=cfg["jitter_speed_max"], extra_damp_factor=cfg["extra_damp_factor"])
    
    ema = AdaptiveEMA(ema_params)
    tremor = TremorGuard(tremor_params)
    profiler = LatencyProfiler(cfg["profiler_log_interval_sec"])
    engine = HookEngine(ema, tremor, profiler, cfg["magic_number"])
    engine.enabled = cfg.get("enabled_on_start", True)
    
    hk = Hotkeys(cfg["hotkey_toggle"], cfg["hotkey_quit"])

    blacklist = [item for item in cfg.get("blacklist", []) if item]
    monitor_thread = None
    stop_event = None
    if blacklist:
        try:
            import psutil  # type: ignore[import-not-found]
            import win32gui  # type: ignore[import-not-found]
            import win32process  # type: ignore[import-not-found]
        except ImportError as exc:
            print(f"Monitoramento de processos indisponível ({exc}). Instale psutil e pywin32 para habilitar a blacklist.")
        else:
            stop_event = threading.Event()
            monitor_thread = threading.Thread(
                target=monitor_foreground_process,
                args=(engine, blacklist, stop_event, win32gui, win32process, psutil),
                daemon=True,
            )
            monitor_thread.start()

    # 2. Bloco Try...Finally para garantir que os hooks e hotkeys sejam sempre desregistrados
    try:
        engine.install()
        hk.register()

        print("\nSuavizador de Mira ativo e rodando.")
        print("Pressione a hotkey de Ligar/Desligar para pausar/retomar.")
        print("Pressione a hotkey de Sair para fechar o aplicativo.\n")

        if cfg.get("run_calibration_on_start", False):
            print("Iniciando calibração guiada...")
            run_calibration(
                engine,
                ema,
                slow_duration_sec=cfg.get("calibration_slow_duration_sec", 5.0),
                fast_duration_sec=cfg.get("calibration_fast_duration_sec", 5.0),
            )
            print("Calibração finalizada.")

        # 3. Inicia o loop de mensagens do Windows.
        msg = wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id == ID_TOGGLE_HOTKEY:
                    status = "ATIVADO" if engine.toggle_user_enabled() else "DESATIVADO"
                    print(f"Filtro de suavizacao: {status}")
                elif hotkey_id == ID_QUIT_HOTKEY:
                    print("Hotkey de saida pressionada. Encerrando...")
                    ctypes.windll.user32.PostQuitMessage(0)

            ctypes.windll.user32.TranslateMessage(byref(msg))
            ctypes.windll.user32.DispatchMessageW(byref(msg))

    except OSError as e:
        print(f"Erro fatal da API do Windows: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        # 4. Limpeza.
        print("\nEncerrando. Realizando limpeza...")
        if stop_event:
            stop_event.set()
        if monitor_thread:
            monitor_thread.join(timeout=1.5)
        engine.resume("blacklist")
        hk.unregister()
        engine.uninstall()
        print("Limpeza concluída. Adeus!")

if __name__ == "__main__":
    main()
