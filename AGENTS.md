# AimSmoother Architecture and Agents

**Disclaimer:** This document describes the architecture of a proof-of-concept project. It is intended for educational and experimental purposes.

This document describes the architecture of AimSmoother, detailing each of its components (or "agents") and how they interact to provide the aim smoothing functionality.

## Architectural Overview

AimSmoother operates based on a linear, low-latency data flow. The architecture is designed to be modular, with each component having a unique responsibility.

The data flow can be represented as follows:

```
[Mouse Input] -> [1. Hook Agent] -> [2. Tremor Guard] -> [3. Smoothing Agent] -> [4. Injection Agent] -> [OS]
                                          ^
                                          |
                                    [5. Hotkey Agent]
                                          |
                                          v
                                  [Activation Control]
```

## The Agents

### 1. Hook Agent (`win_hook.py`)

*   **Responsibility:** To intercept all raw mouse movement events system-wide.
*   **Implementation:** Uses the `SetWindowsHookExA` function from the Windows API to register a low-level mouse hook (`WH_MOUSE_LL`). This ensures that it captures mouse data before most applications.
*   **Functioning:** This is the entry point for raw mouse data into the system. It captures the cursor's delta movements `(dx, dy)` and the time since the last event `(dt)`. It then passes this data to the next agent in the pipeline. If smoothing is disabled via the hotkey, this agent simply calls the next hook in the chain, bypassing the smoothing pipeline entirely.

### 2. Tremor Guard (`tremor.py`)

*   **Responsibility:** To act as a pre-filter, distinguishing between unwanted jitter and intentional slow movements.
*   **Implementation:** The `TremorGuard` class implements a deadzone and an extra damping mechanism.
*   **Functioning:** This agent receives the raw `(dx, dy, dt)` from the Hook Agent. It performs two checks:
    1.  **Deadzone:** It calculates the speed and magnitude of the movement. If the speed is below `jitter_speed_max` and the magnitude is within `jitter_deadzone_px`, the movement is classified as noise, and the deltas are zeroed out.
    2.  **Extra Damping:** For movements that are very slow but intentional (i.e., outside the deadzone), it calculates a `gain` factor. This factor is less than 1.0 and will be used by the main smoothing agent to apply even more aggressive smoothing.
    The processed deltas and the `gain` factor are then passed to the Smoothing Agent.

### 3. Smoothing Agent (`smoothing.py`)

*   **Responsibility:** To apply the core adaptive smoothing algorithm.
*   **Implementation:** The `AdaptiveEMA` class uses an Exponential Moving Average filter whose smoothing factor is dynamically adjusted based on velocity.
*   **Functioning:** This agent receives the data from the Tremor Guard. It calculates the current mouse speed and uses this value to determine the appropriate smoothing factor, `alpha`. This is done by linearly interpolating between a minimum alpha (`alpha_min`, for slow speeds) and a maximum alpha (`alpha_max`, for high speeds), based on where the current speed falls between `v_min` and `v_max`. The final `alpha` is then multiplied by the `gain` from the Tremor Guard for additional damping. The EMA formula is then applied to the `dx` and `dy` values separately, resulting in a smoothed output.

### 4. Injection Agent (`injector.py`)

*   **Responsibility:** To inject the final, smoothed mouse movement back into the operating system.
*   **Implementation:** Uses the `SendInput` function from the Windows API to create a synthetic mouse input event.
*   **Functioning:** This is the final stage of the pipeline. It receives the smoothed `(dx, dy)` from the Smoothing Agent and sends it to the OS. This new movement event replaces the original one that was intercepted by the Hook Agent.

### 5. Hotkey Agent (`hotkeys.py`)

*   **Responsibility:** To provide a simple, system-wide toggle for the smoothing functionality.
*   **Implementation:** Monitors keyboard input for a specific key combination (e.g., `Ctrl+Alt+S`).
*   **Functioning:** When the hotkey is detected, it flips a boolean flag in the main orchestrator. This flag is checked by the Hook Agent to determine whether to activate the smoothing pipeline or to pass the mouse input through without modification.

### Other Components

*   **`__main__.py` (Orchestrator):** The central nervous system of the application. It is responsible for:
    *   Reading the `config/defaults.json` file to load all parameters.
    *   Instantiating all the agents.
    *   Connecting the agents in the correct pipeline order.
    *   Initializing the hotkey listener.
    *   Starting the Windows message loop, which is required for the hook to function.

*   **`profiler.py` (Latency Profiler):** A diagnostic tool that wraps the processing pipeline (from hook to injection) and measures the execution time. This is crucial for development and debugging to ensure that the smoothing process does not introduce any noticeable input lag.
