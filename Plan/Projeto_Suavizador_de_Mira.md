# Project Hub v8.0 - A Edição Definitiva

**Documento:** Hub de Projeto e Blueprint de Implementação Total
**Versão:** 8.0
**Propósito:** Unir passado, presente e futuro em um único documento mestre. Esta é a especificação mais exaustiva e contextualizada possível, detalhando não apenas o MVP já codificado, mas também a implementação granular de cada funcionalidade futura até a versão 1.0, para que o caminho para um aplicativo "perfeito" seja claro e inequívoco.

---

## Seção 1: Status e Histórico do Projeto

### 1.1. O Que Já Fizemos (Conquistas ✅)

*   **[✅ CONCLUÍDO] Fase 1-2: Análise e Planejamento Arquitetural**
    *   `[✅]` Análise de engenharia reversa do "Custom Curve Pro" e definição da arquitetura de Hook, Processamento e Injeção via `ctypes`.
    *   `[✅]` Criação de múltiplos blueprints (v1 a v5), culminando em um design que inclui um profiler de latência para garantir performance mensurável.

*   **[✅ CONCLUÍDO] Fase 3: Setup do Ambiente**
    *   `[✅]` Criação da estrutura completa de pastas (`AimSmoother`, `src`, `config`) e arquivos do projeto.

*   **[✅ CONCLUÍDO] Fase 4: Implementação do Código-Fonte do MVP**
    *   `[✅]` Todos os módulos (`injector`, `profiler`, `smoothing`, `tremor`, `hotkeys`, `win_hook`, `__main__`) foram codificados e salvos, resultando em um aplicativo de console funcional.

### 1.2. Onde Estamos Agora (Tarefa Atual ➡️)

*   **[➡️ EM ANDAMENTO] Fase 5: Testes e Validação do MVP.**
    *   **TAREFA ATUAL:** Executar o aplicativo (`python -m src`) para realizar o plano de testes manuais e analisar os dados de latência do profiler. Esta validação é o portão de qualidade para todo o desenvolvimento futuro.

---

## Seção 2: O Que Falta Fazer - Roadmap de Implementação Ultra-Detalhado

Esta seção detalha o "como" de cada passo futuro, com checklists, análises de implementação e pseudo-código.

### **[⬜️ PENDENTE] Milestone 1: v0.2 - O App Inteligente (Usabilidade e Segurança)**

*   **Feature 1: Assistente de Calibração Guiada.**
    *   **Objetivo:** Abstrair 100% da complexidade de configuração do usuário.
    *   **Análise de Implementação Detalhada:**
        *   **Dependências:** `tkinter` (para a UI), que é nativo do Python.
        *   **Gerenciamento de Estado:** O `HookEngine` precisará de um novo atributo, `self.mode`, que pode ser `'smoothing'`, `'calibrating_slow'`, ou `'calibrating_fast'`. O comportamento do `_callback` mudará drasticamente com base nesse estado.
        *   **Fluxo de Controle:** A função `main` chamará uma nova função `run_calibration()`. Esta função será responsável por toda a UX da calibração.
    *   **Checklist de Implementação Detalhado:**
        *   `[⬜️]` **`calibration_ui.py`:** Criar um novo arquivo para a classe `CalibrationWindow`.
            *   `[⬜️]` A classe usará `tkinter.Toplevel` para criar a janela.
            *   `[⬜️]` Conterá um `tkinter.Label` para as instruções e um `ttk.Progressbar`.
            *   `[⬜️]` Terá métodos como `show_slow_phase()`, `show_fast_phase()`, `close_window()`.
        *   `[⬜️]` **`win_hook.py`:** Modificar a classe `HookEngine`.
            *   `[⬜️]` Adicionar `self.mode = 'smoothing'` e `self.calibration_data = {}` ao `__init__`.
            *   `[⬜️]` Modificar o `_callback` para não fazer nada (apenas `CallNextHookEx`) se o modo não for `'smoothing'`. Em vez disso, a coleta de dados será feita em um `callback` separado e mais simples, para não poluir o caminho crítico.
        *   `[⬜️]` **`__main__.py`:** Implementar a lógica de orquestração.
            *   `[⬜️]` Criar a função `run_calibration(engine, ui)`.
            *   **Pseudo-código para `run_calibration`:**
                ```python
                def run_calibration(engine, ui):
                    ui.show_instruction("Prepare-se para a fase LENTA...")
                    ui.after(3000, lambda: start_slow_collection(engine, ui))
                
                def start_slow_collection(engine, ui):
                    engine.start_slow_calibration() # Seta o modo e limpa dados
                    ui.show_instruction("Mova o mouse lentamente por 5s...")
                    ui.start_progressbar(5000)
                    ui.after(5000, lambda: start_fast_phase(engine, ui))
                
                # ... e assim por diante para a fase rápida e o cálculo final ...
                ```

*   **Feature 2: Blacklist de Processos.**
    *   **Objetivo:** Aumentar a segurança e a paz de espírito do usuário.
    *   **Análise de Implementação Detalhada:**
        *   **Dependências:** `pywin32` e `psutil`. Ambas precisam ser adicionadas ao `requirements.txt`.
        *   **Threading:** A checagem precisa rodar em um thread separado para não bloquear o loop de mensagens principal. O thread deve ser `daemon=True` para fechar junto com o programa.
    *   **Checklist de Implementação Detalhado:**
        *   `[⬜️]` **`requirements.txt`:** Adicionar `pywin32` e `psutil`.
        *   `[⬜️]` **`defaults.json`:** Adicionar a chave `"blacklist": ["valorant.exe"]`.
        *   `[⬜️]` **`__main__.py`:**
            *   `[⬜️]` Importar `threading`, `time`, `win32gui`, `win32process`, `psutil`.
            *   `[⬜️]` Criar a função `monitor_foreground_process(engine, stop_event)`.
            *   `[⬜️]` Na função `main`, iniciar o thread: `stop_event = threading.Event()`, `monitor_thread = threading.Thread(target=..., args=(engine, stop_event), daemon=True)`, `monitor_thread.start()`.
            *   `[⬜️]` No bloco `finally`, chamar `stop_event.set()` para sinalizar o encerramento do thread.
        *   `[⬜️]` **`win_hook.py`:**
            *   `[⬜️]` Adicionar os métodos `pause()` e `resume()` à classe `HookEngine`, que simplesmente alteram o valor de `self.enabled` (com lógica para lembrar o estado anterior).

### **[⬜️ PENDENTE] Milestone 2: v0.3 - A Interface de Controle**

*   **Feature 3: Painel de Controle em Tempo Real.**
    *   **Objetivo:** Empoderar o usuário avançado com personalização intuitiva.
    *   **Análise de Implementação Detalhada:**
        *   **Dependências:** `matplotlib`.
        *   **Arquitetura da UI:** A UI (`control_panel_ui.py`) não deve conter lógica de negócio. Ela apenas lê os valores iniciais, e quando um slider é movido, ela chama uma função de `callback` passada pelo `__main__.py`.
    *   **Checklist de Implementação Detalhado:**
        *   `[⬜️]` **`requirements.txt`:** Adicionar `matplotlib`.
        *   `[⬜️]` **`control_panel_ui.py`:**
            *   `[⬜️]` Criar a classe `ControlPanelWindow`.
            *   `[⬜️]` Implementar a incorporação de um `FigureCanvasTkAgg` do Matplotlib na janela Tkinter.
            *   `[⬜️]` Criar os widgets `ttk.Scale` para cada parâmetro, configurando seus `command` para chamar as funções de callback.
        *   `[⬜️]` **`__main__.py`:**
            *   `[⬜️]` Criar as funções de callback, ex: `def on_vmax_changed(new_value): engine.ema.params.v_max = float(new_value); ui.redraw_graph()`.
            *   `[⬜️]` Passar essas funções para a instância da UI.

### **[⬜️ PENDENTE] Milestone 3: v1.0 - O Produto Polido**

*   **Feature 4, 5, 6: Autonomia e Distribuição.**
    *   **Objetivo:** Transformar o script em um aplicativo de desktop completo e autônomo.
    *   **Análise de Implementação Detalhada:**
        *   **System Tray:** A biblioteca `pystray` é a mais indicada. Ela cria seu próprio loop, então a lógica do `__main__.py` precisará ser refatorada para se integrar a ele, em vez de usar um loop de mensagens Tkinter ou `ctypes`.
        *   **Inicialização com Windows:** O módulo `winreg` é a forma correta e nativa de fazer isso, evitando arquivos `.bat` ou atalhos na pasta de inicialização.
        *   **PyInstaller:** A chave é um arquivo `.spec` bem configurado. Ele precisará usar a opção `datas` para empacotar o `defaults.json` e o arquivo de ícone (`.ico`) junto com o executável.
    *   **Checklist de Implementação Detalhado:**
        *   `[⬜️]` **`requirements.txt`:** Adicionar `pystray`.
        *   `[⬜️]` **`__main__.py`:** Refatorar o ponto de entrada para usar `pystray.Icon` e definir seu menu e callbacks.
        *   `[⬜️]` **`settings.py` (Novo Módulo):** Criar um módulo para gerenciar a lógica de registro (ex: `toggle_startup(enable: bool)`).
        *   `[⬜️]` **`build.spec` (Novo Arquivo):** Criar o arquivo de especificação do PyInstaller, testando o build para garantir que o `.exe` final seja autônomo e funcione em outras máquinas.

---

Este Hub v8.0 é o documento mais completo que podemos criar. Ele une a jornada que fizemos com um guia de implementação passo a passo, função por função, para o futuro. Cada detalhe está aqui. A próxima ação não é mais planejar, é executar a **Tarefa Atual**: validar o MVP que já está codificado.