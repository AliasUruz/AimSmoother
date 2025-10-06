import ctypes
import json
import sys
from pathlib import Path
from ctypes import wintypes, byref

# Importa todos os nossos módulos
from .smoothing import AdaptiveEMA, LinearEMAParams
from .tremor import TremorGuard, TremorParams
from .win_hook import HookEngine
from .hotkeys import Hotkeys, ID_TOGGLE_HOTKEY, ID_QUIT_HOTKEY
from .profiler import LatencyProfiler

# Constante para a mensagem de hotkey do Windows
WM_HOTKEY = 0x0312

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

    # 2. Bloco Try...Finally para garantir que os hooks e hotkeys sejam sempre desregistrados
    try:
        engine.install()
        hk.register()

        print("\nSuavizador de Mira ativo e rodando.")
        print("Pressione a hotkey de Ligar/Desligar para pausar/retomar.")
        print("Pressione a hotkey de Sair para fechar o aplicativo.\n")

        # 3. Inicia o loop de mensagens do Windows.
        msg = wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id == ID_TOGGLE_HOTKEY:
                    engine.enabled = not engine.enabled
                    status = "ATIVADO" if engine.enabled else "DESATIVADO"
                    print(f"Filtro de suavização: {status}")
                elif hotkey_id == ID_QUIT_HOTKEY:
                    print("Hotkey de saída pressionada. Encerrando...")
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
        hk.unregister()
        engine.uninstall()
        print("Limpeza concluída. Adeus!")

if __name__ == "__main__":
    main()