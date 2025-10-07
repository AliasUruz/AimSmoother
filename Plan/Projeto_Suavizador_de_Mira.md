# Project Hub v9.0 - Estrutura Aprimorada

**Documento:** Centro de planejamento e trilha de execucao
**Versao:** 9.0
**Objetivo:** Consolidar o historico, registrar as conquistas mais recentes (assistente de calibracao e blacklist ativa) e alinhar o roteiro tecnico ate a versao 1.0 com tarefas acionaveis.

---

## 1. Instantaneo do Projeto

### 1.1 Entregas consolidadas
- [x] Fase 1-2: Arquitetura validada (hook -> tremor -> smoothing -> injector) e comunicacao via ctypes.
- [x] Fase 3: Estrutura de pastas, configuracao JSON e hotkeys registradas.
- [x] Fase 4: MVP funcional com TremorGuard, Adaptive EMA, profiler de latencia e pipeline completo.
- [x] Fase 5: Validacao inicial do MVP e hardening de usabilidade.
  - Assistente de calibracao guiada em Tk (coleta de fase lenta/rapida, ajuste automatico de v_min/v_max).
  - Monitor de processos com pausa/resume automatico via blacklist (ex.: valorant.exe) e mensagens de status.
  - Configuracoes novas expostas em `config/defaults.json` e dependencias adicionadas (`psutil`, `pywin32`).

### 1.2 Estado atual (gate de progresso)
- [ ] Coletar feedback manual da calibracao (confirmar se os valores ajustados agradam diferentes perfis de usuario).
- [ ] Validar o monitoramento em cenarios edge (multi-monitor, jogos em modo borderless, processos com privilegios elevados).
- [ ] Documentar fluxo de encerramento seguro quando o app foi pausado por blacklist.


## 2. Plano de trabalho imediato (proxima iteracao sugerida)
1. **Persistencia opcional da calibracao**
   - Permitir gravar os parametros sugeridos em arquivo (novo `calibration_results.json`) ou reaplicar automaticamente no proximo boot.
   - Adicionar botao "Aplicar"/"Cancelar" no assistente para dar controle ao usuario sobre a atualizacao.
2. **Telemetria de latencia aprofundada**
   - Registrar stats basicas (media/p95 do pipeline) a cada X segundos e imprimir um resumo sintetico.
   - Preparar hooks para enviar os dados ao futuro painel de controle.
3. **Fail-safes da blacklist**
   - Caso o processo bloqueado finalize sem perder o foco (crash), garantir que o resume seja disparado.
   - Acrescentar testes rapidos: executar `monitor_foreground_process` diretamente via script para validar estados (pausado/religado).


## 3. Roadmap Detalhado ate a v1.0

### Milestone 2: v0.3 - Painel de Controle em Tempo Real
- **Objetivo:** Ajustes dinamicos dos parametros e visualizacao da curva de resposta.
- **Arquitetura proposta:**
  - Novo modulo `control_panel_ui.py` em Tkinter + Matplotlib (usar FigureCanvasTkAgg).
  - Comunicar-se com o core via callbacks para atualizar `AdaptiveEMA.params` e `TremorGuard` em tempo real.
- **Tarefas tecnicas:**
  1. Carregar configuracoes atuais e exibir em sliders (`ttk.Scale`) com limites seguros (ex.: `alpha_min` entre 0.01 e 0.3).
  2. Plotar grafico da curva v -> alpha, atualizando a cada alteracao.
  3. Adicionar secao de diagnostico exibindo:
     - estado do hook (rodando/pausado/blacklist);
     - ultima leitura do profiler (media/pico em microsegundos).
  4. Integrar com o assistente de calibracao para permitir relancar a coleta diretamente do painel (botao "Recalibrar").
- **Criterios de aceite:** UI nao trava a thread principal; ajustar slider reflete de imediato no movimento; logs claros de validacao.

### Milestone 3: v1.0 - Produto Polido
- **Objetivo:** Empacotar, iniciar com o Windows e entregar UX desktop.
- **Componentes chave:**
  1. **System Tray (pystray):**
     - Menu com opcoes: Ativar/Desativar, Abrir painel, Recalibrar, Sair.
     - Ajustar `__main__.py` para conviver com o loop da bandeja e com o painel Tkinter.
  2. **Startup com Windows:**
     - Novo modulo `settings.py` para inspecionar/adicionar entradas no `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
     - Persistir preferencia do usuario (checkbox no painel + confirmacao).
  3. **Empacotamento (PyInstaller):**
     - Criar `build.spec` com inclusao de `config/defaults.json`, calibracao (se houver), assets do tray.
     - Pipeline de smoke test: executar o executavel gerado e validar hook, hotkeys, calibracao e blacklist.

### Backlog estendido (pos v1.0)
- Modo "perfil" com pre-sets (casual, competitivo, acesso facilitado).
- Integracao com API de jogo (quando permitido) para ajustar smoothing conforme contexto (ex.: ADS vs hip-fire).
- Canal opcional de atualizacao automatica.


## 4. Riscos e Contencoes Prioritarios
- **Compatibilidade com anti-cheat:** manter lista de processos sensiveis (Valorant, Apex, COD) documentada; adicionar opcao de whitelist manual.
- **Latencia adicional inadvertida:** usar o profiler para garantir <0.5 ms mesmo com painel aberto; caso exceda, ativar modo "lite" que desliga graficos em tempo real.
- **Concorrencia com Tkinter:** encapsular chamadas de UI em threads dedicadas e usar `queue` + `after` para comunicacao segura.
- **Depedencias externas:** monitorar instalacao de `pywin32` e `psutil`; sugerir `python -m pip install -r requirements.txt` na documentacao oficial.


## 5. Referencias Rapidas e Itens de Apoio
- **Hotkeys atuais:** toggle por `F10`, sair por `F12`.
- **Parametros sugeridos pos-calibracao:** conferidos via `AdaptiveEMA.params` no console apos rodar o assistente.
- **Scripts uteis:** executar `python -m src` para iniciar o app; `python -m compileall src` para garantir que o codigo compila apos alteracoes.
- **Checklist de encerramento:**
  1. Garantir que `stop_event` foi sinalizado e `engine.resume("blacklist")` chamado.
  2. Verificar mensagens do monitor para confirmar que nao ha pausas pendentes.
  3. Encerrar a janela do painel (quando existir) antes do `Ctrl+C`.

---

Este Hub v9.0 mantem o DNA das versoes anteriores, mas traz contexto adicional, criterios de aceite e tarefas diretamente acionaveis. Use este documento como guia vivo: marque concluido, ajuste prioridades e anote feedbacks vindos dos testes de campo.
