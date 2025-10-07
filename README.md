# AimSmoother: Adaptive Aim Smoother for Windows

**Disclaimer:** This is a proof-of-concept project and not a finished product. It is intended for educational and experimental purposes. Use at your own risk.

**AimSmoother** is an open-source application for Windows that applies a real-time smoothing filter to mouse movement. The goal is to correct involuntary hand tremors, providing a more stable and precise aim in games without compromising the ability to make fast, intentional movements. This tool is primarily designed for gamers but can be used by anyone who needs a smoother mouse experience.

## Features

### Current (MVP)

*   **Advanced Adaptive Smoothing:** Utilizes a sophisticated two-stage filtering system:
    1.  **Tremor Guard:** A pre-filter that uses a deadzone to eliminate small, unintentional movements (jitter) and applies extra damping to very slow movements.
    2.  **Adaptive EMA:** An Exponential Moving Average (EMA) filter that dynamically adjusts the smoothing factor based on the mouse speed. More smoothing is applied to slow movements and less to fast movements.
*   **Global Mouse Hook:** Intercepts mouse movement throughout the operating system, working with any game or application.
*   **JSON Configuration:** Allows for easy adjustment of all smoothing parameters through a `defaults.json` file.
*   **Hotkeys:** Enable or disable smoothing at any time with a key combination (default: `Ctrl+Alt+S`).
*   **Latency Profiler:** Integrated tool to measure the performance impact of the application.
*   **Guided Calibration Wizard:** Launches on startup (configurable) to collect slow and fast motion profiles and auto-tune the smoothing curve.
*   **Process Blacklist:** Monitors the foreground process and automatically pauses smoothing whenever a protected executable (e.g., `valorant.exe`) is detected.

### Planned (Roadmap)

*   **Real-Time Control Panel:** A GUI to adjust smoothing parameters and visualize the mouse response graph.
*   **System Tray Integration and Start with Windows.**
*   **Packaging as a standalone executable.**

## How it Works

AimSmoother operates in a three-stage pipeline designed for minimal latency:

1.  **Hook:** The `win_hook.py` module uses the Windows API (`SetWindowsHookExA`) to intercept raw mouse movement data at a low level.
2.  **Process:** The captured data is then processed by a two-stage filtering system:
    *   **`tremor.py` (Tremor Guard):** This pre-filter first analyzes the movement. If the movement is very small and slow, it's considered jitter and discarded. If it's a slow, intentional movement, a damping factor is calculated.
    *   **`smoothing.py` (Adaptive EMA):** The main smoothing filter receives the (potentially modified) mouse data. It calculates the mouse speed and uses it to linearly interpolate a smoothing factor (`alpha`) between a minimum and maximum value. This adaptive `alpha`, combined with the damping factor from the Tremor Guard, is used in an EMA formula to produce the final, smoothed mouse coordinates.
3.  **Inject:** The `injector.py` module takes the smoothed coordinates and uses the Windows API (`SendInput`) to inject them back into the system, replacing the original, shaky movement.

This entire process is orchestrated by `__main__.py`, which also handles loading settings from `config/defaults.json` and managing hotkeys.

## Getting Started

### Prerequisites

*   Python 3.x

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/AimSmoother.git
    cd AimSmoother
    ```

2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Execution

To start the application, run the following command in the terminal:

```bash
python -m src
```

The application will run in the background. You can use the `Ctrl+Alt+S` hotkey to enable or disable smoothing. To close the. application, press `Ctrl+C` in the terminal.

## Configuration

You can customize the behaviour of AimSmoother by editing the `config/defaults.json` file:

*   **Smoothing:** `v_min`, `v_max`, `alpha_min`, `alpha_max` control how the adaptive EMA reacts to mouse speed.
*   **Tremor Guard:** `jitter_deadzone_px`, `jitter_speed_max`, `extra_damp_factor` define the jitter rejection and additional damping.
*   **Calibration:** `run_calibration_on_start` toggles the guided wizard. `calibration_slow_duration_sec` and `calibration_fast_duration_sec` set the duration (in seconds) of each phase.
*   **Hotkeys:** `hotkey_toggle` and `hotkey_quit` customise the global shortcuts.
*   **Process Blacklist:** Populate the `blacklist` array with executable names (e.g., `"valorant.exe"`) to pause smoothing automatically whenever those processes are in the foreground.
*   **Misc:** `enabled_on_start`, `magic_number`, and `profiler_log_interval_sec` adjust startup defaults and diagnostics.

## Roadmap

The development of AimSmoother is divided into the following milestones:

*   **v0.2 - The Smart App:** Focus on usability and security, with the implementation of the calibration wizard and process blacklist.
*   **v0.3 - The Control Interface:** Creation of a real-time control panel for advanced customization.
*   **v1.0 - The Polished Product:** Transform the script into a complete desktop application, with an installer, system tray icon, and startup with Windows.

## Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, feel free to open an *issue* or submit a *pull request*.

## License

This project is licensed under the [MIT License](LICENSE).
