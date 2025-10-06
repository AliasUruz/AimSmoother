# AimSmoother Architecture and Agents

**Disclaimer:** This document describes the architecture of a proof-of-concept project. It is intended for educational and experimental purposes.

This document describes the architecture of AimSmoother, detailing each of its components (or "agents") and how they interact to provide the aim smoothing functionality.

## Architectural Overview

AimSmoother operates based on a linear, low-latency data flow. The architecture is designed to be modular, with each component having a unique responsibility.

The data flow can be represented as follows:

```
[Mouse Input] -> [1. Hook Agent] -> [2. Smoothing Agent] -> [3. Injection Agent] -> [Operating System]
      ^
      |
[4. Hotkey Agent]
      |
      v
[Activation Control]
```

## The Agents

### 1. Hook Agent (`win_hook.py`)

*   **Responsibility:** Intercept mouse movement throughout the system.
*   **Implementation:** Uses the `SetWindowsHookExA` function from the Windows API to register a callback that is called whenever the mouse moves.
*   **Functioning:** This is the entry point for raw mouse data into the system. It captures the cursor's `(x, y)` coordinates and passes them to the next agent in the pipeline.

### 2. Smoothing Agent (`smoothing.py`)

*   **Responsibility:** Apply the adaptive smoothing algorithm.
*   **Implementation:** Contains the logic for the Exponential Moving Average (EMA). The agent maintains an internal state of the previous mouse position to calculate the speed and adjust the smoothing factor.
*   **Functioning:** Receives the raw coordinates from the Hook Agent. Based on the movement speed, it applies a higher or lower smoothing factor, calculating the new smoothed position. The goal is to filter out tremor (small, fast movements) without adding a noticeable delay to intentional movements.

### 3. Injection Agent (`injector.py`)

*   **Responsibility:** Inject the smoothed movement back into the system.
*   **Implementation:** Uses the `SendInput` function from the Windows API to simulate mouse movement.
*   **Functioning:** Receives the smoothed coordinates from the Smoothing Agent and sends them to the operating system as if they were the original mouse input. This effectively replaces the irregular movement with the filtered movement.

### 4. Hotkey Agent (`hotkeys.py`)

*   **Responsibility:** Allow the user to enable or disable smoothing.
*   **Implementation:** Monitors the keyboard for a specific key combination (e.g., `Ctrl+Alt+S`).
*   **Functioning:** When the hotkey is pressed, it toggles a global state that is checked by the Hook Agent. If smoothing is disabled, the Hook Agent simply passes the raw mouse data to the system without sending it to the Smoothing Agent.

### Other Components

*   **`__main__.py` (Orchestrator):**
    *   Initializes all agents and connects them.
    *   Loads the configuration from `defaults.json`.
    *   Starts the Windows message loop, which keeps the application running and allows the hooks to work.

*   **`profiler.py` (Latency Profiler):**
    *   A diagnostic agent that measures the time elapsed between capturing the movement (Hook) and its injection (Injection).
    *   It is essential to ensure that the smoothing process does not introduce a noticeable latency that could harm the gaming experience.

*   **`config/defaults.json` (Configuration):**
    *   A configuration file that allows the end-user (or future agents, such as the control panel) to adjust the parameters of the Smoothing Agent without needing to change the source code.