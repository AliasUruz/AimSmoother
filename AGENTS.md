# Arquitetura e Agentes do AimSmoother

Este documento descreve a arquitetura do AimSmoother, detalhando cada um dos seus componentes (ou "agentes") e como eles interagem para fornecer a funcionalidade de suavização de mira.

## Visão Geral da Arquitetura

O AimSmoother opera com base em um fluxo de dados linear e de baixa latência. A arquitetura é projetada para ser modular, com cada componente tendo uma responsabilidade única.

O fluxo de dados pode ser representado da seguinte forma:

```
[Entrada do Mouse] -> [1. Hook Agent] -> [2. Smoothing Agent] -> [3. Injection Agent] -> [Sistema Operacional]
        ^
        |
[4. Hotkey Agent]
        |
        v
[Controle de Ativação]
```

## Os Agentes

### 1. Hook Agent (`win_hook.py`)

*   **Responsabilidade:** Interceptar o movimento do mouse em todo o sistema.
*   **Implementação:** Utiliza a função `SetWindowsHookExA` da API do Windows para registrar um *callback* que é chamado sempre que o mouse se move.
*   **Funcionamento:** Este é o ponto de entrada dos dados brutos do mouse no sistema. Ele captura as coordenadas `(x, y)` do cursor e as passa para o próximo agente no pipeline.

### 2. Smoothing Agent (`smoothing.py`)

*   **Responsabilidade:** Aplicar o algoritmo de suavização adaptativa.
*   **Implementação:** Contém a lógica para a Média Móvel Exponencial (EMA). O agente mantém um estado interno da posição anterior do mouse para calcular a velocidade e ajustar o fator de suavização.
*   **Funcionamento:** Recebe as coordenadas brutas do *Hook Agent*. Com base na velocidade do movimento, ele aplica um fator de suavização maior ou menor, calculando a nova posição suavizada. O objetivo é filtrar o tremor (movimentos pequenos e rápidos) sem adicionar um atraso perceptível aos movimentos intencionais.

### 3. Injection Agent (`injector.py`)

*   **Responsabilidade:** Injetar o movimento suavizado de volta no sistema.
*   **Implementação:** Utiliza a função `SendInput` da API do Windows para simular um movimento do mouse.
*   **Funcionamento:** Recebe as coordenadas suavizadas do *Smoothing Agent* e as envia para o sistema operacional como se fossem a entrada original do mouse. Isso efetivamente substitui o movimento irregular pelo movimento filtrado.

### 4. Hotkey Agent (`hotkeys.py`)

*   **Responsabilidade:** Permitir que o usuário ative ou desative a suavização.
*   **Implementação:** Monitora o teclado para uma combinação de teclas específica (ex: `Ctrl+Alt+S`).
*   **Funcionamento:** Quando a hotkey é pressionada, ela alterna um estado global que é verificado pelo *Hook Agent*. Se a suavização estiver desativada, o *Hook Agent* simplesmente passa os dados brutos do mouse para o sistema sem enviá-los ao *Smoothing Agent*.

### Outros Componentes

*   **`__main__.py` (Orquestrador):**
    *   Inicializa todos os agentes e os conecta.
    *   Carrega a configuração do `defaults.json`.
    *   Inicia o loop de mensagens do Windows, que mantém o aplicativo em execução e permite que os hooks funcionem.

*   **`profiler.py` (Profiler de Latência):**
    *   Um agente de diagnóstico que mede o tempo decorrido entre a captura do movimento (Hook) e a sua injeção (Injection).
    *   É essencial para garantir que o processo de suavização não introduza uma latência perceptível que possa prejudicar a experiência de jogo.

*   **`config/defaults.json` (Configuração):**
    *   Um arquivo de configuração que permite ao usuário final (ou a futuros agentes, como o painel de controle) ajustar os parâmetros do *Smoothing Agent* sem precisar alterar o código-fonte.
