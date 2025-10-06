# AimSmoother: Suavizador de Mira Adaptativo para Windows

**AimSmoother** é um aplicativo de código aberto para Windows que aplica um filtro de suavização em tempo real ao movimento do mouse. O objetivo é corrigir tremores involuntários da mão, proporcionando uma mira mais estável e precisa em jogos, sem comprometer a capacidade de realizar movimentos rápidos e intencionais.

## Funcionalidades

### Atuais (MVP)

*   **Suavização Adaptativa:** Utiliza um algoritmo de Média Móvel Exponencial (EMA) que se ajusta à velocidade do mouse, aplicando mais suavização a movimentos lentos (tremores) e menos a movimentos rápidos.
*   **Hook Global de Mouse:** Intercepta o movimento do mouse em todo o sistema operacional, funcionando com qualquer jogo ou aplicativo.
*   **Configuração via JSON:** Permite ajustar facilmente os parâmetros de suavização através de um arquivo `defaults.json`.
*   **Hotkeys:** Ative ou desative a suavização a qualquer momento com uma combinação de teclas (padrão: `Ctrl+Alt+S`).
*   **Profiler de Latência:** Ferramenta integrada para medir o impacto de performance do aplicativo.

### Planejadas (Roadmap)

*   **Assistente de Calibração Guiada:** Uma interface para ajudar o usuário a encontrar as configurações ideais de forma automática.
*   **Painel de Controle em Tempo Real:** Uma GUI para ajustar os parâmetros de suavização e visualizar o gráfico de resposta do mouse.
*   **Blacklist de Processos:** Impedir que o aplicativo funcione com jogos específicos que possam ter políticas anti-cheat restritivas.
*   **Integração com a Bandeja do Sistema e Inicialização com o Windows.**
*   **Empacotamento como um executável autônomo.**

## Como Funciona

O AimSmoother opera em três estágios principais:

1.  **Hook:** Utiliza a API do Windows (`SetWindowsHookExA`) para interceptar os dados brutos de movimento do mouse em baixo nível.
2.  **Processamento:** Um algoritmo de suavização calcula a nova posição do cursor. A suavização é adaptativa, baseada na velocidade atual do mouse, garantindo que movimentos rápidos não sejam afetados negativamente.
3.  **Injeção:** O movimento suavizado é então injetado de volta no sistema, substituindo o movimento original.

Este processo é otimizado para ter a menor latência possível, garantindo uma experiência fluida e responsiva.

## Começando

### Pré-requisitos

*   Python 3.x

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/AimSmoother.git
    cd AimSmoother
    ```

2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Execução

Para iniciar o aplicativo, execute o seguinte comando no terminal:

```bash
python -m src
```

O aplicativo será executado em segundo plano. Você pode usar a hotkey `Ctrl+Alt+S` para ativar ou desativar a suavização. Para fechar o aplicativo, pressione `Ctrl+C` no terminal.

## Configuração

Você pode personalizar os parâmetros de suavização editando o arquivo `config/defaults.json`.

*   `smoothing_factor_slow`: Fator de suavização para movimentos lentos (valores maiores = mais suave).
*   `smoothing_factor_fast`: Fator de suavização para movimentos rápidos (valores menores = menos suave).
*   `speed_threshold`: O limite de velocidade que define um movimento como "rápido".

## Roadmap

O desenvolvimento do AimSmoother está dividido nos seguintes marcos:

*   **v0.2 - O App Inteligente:** Foco em usabilidade e segurança, com a implementação do assistente de calibração e da blacklist de processos.
*   **v0.3 - A Interface de Controle:** Criação de um painel de controle em tempo real para personalização avançada.
*   **v1.0 - O Produto Polido:** Transformar o script em um aplicativo de desktop completo, com instalador, ícone na bandeja do sistema e inicialização com o Windows.

## Contribuição

Contribuições são bem-vindas! Se você tem ideias para novas funcionalidades, melhorias ou correções de bugs, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
