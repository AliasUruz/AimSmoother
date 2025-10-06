# AimSmoother: Adaptive Aim Smoother for Windows

**Disclaimer:** This is a proof-of-concept project and not a finished product. It is intended for educational and experimental purposes. Use at your own risk.

**AimSmoother** is an open-source application for Windows that applies a real-time smoothing filter to mouse movement. The goal is to correct involuntary hand tremors, providing a more stable and precise aim in games without compromising the ability to make fast, intentional movements.

## Features

### Current (MVP)

*   **Adaptive Smoothing:** Uses an Exponential Moving Average (EMA) algorithm that adjusts to the mouse speed, applying more smoothing to slow movements (tremors) and less to fast movements.
*   **Global Mouse Hook:** Intercepts mouse movement throughout the operating system, working with any game or application.
*   **JSON Configuration:** Allows for easy adjustment of smoothing parameters through a `defaults.json` file.
*   **Hotkeys:** Enable or disable smoothing at any time with a key combination (default: `Ctrl+Alt+S`).
*   **Latency Profiler:** Integrated tool to measure the performance impact of the application.

### Planned (Roadmap)

*   **Guided Calibration Wizard:** A UI to help the user find the ideal settings automatically.
*   **Real-Time Control Panel:** A GUI to adjust smoothing parameters and visualize the mouse response graph.
*   **Process Blacklist:** Prevent the application from working with specific games that may have restrictive anti-cheat policies.
*   **System Tray Integration and Start with Windows.**
*   **Packaging as a standalone executable.**

## How it Works

AimSmoother operates in three main stages:

1.  **Hook:** Uses the Windows API (`SetWindowsHookExA`) to intercept raw mouse movement data at a low level.
2.  **Process:** An adaptive smoothing algorithm calculates the new cursor position. The smoothing is adaptive, based on the current mouse speed, ensuring that fast movements are not negatively affected.
3.  **Inject:** The smoothed movement is then injected back into the system, replacing the original movement.

This process is optimized for the lowest possible latency, ensuring a fluid and responsive experience.

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

The application will run in the background. You can use the `Ctrl+Alt+S` hotkey to enable or disable smoothing. To close the application, press `Ctrl+C` in the terminal.

## Configuration

You can customize the smoothing parameters by editing the `config/defaults.json` file.

*   `smoothing_factor_slow`: Smoothing factor for slow movements (higher values = smoother).
*   `smoothing_factor_fast`: Smoothing factor for fast movements (lower values = less smoothing).
*   `speed_threshold`: The speed threshold that defines a movement as "fast".

## Roadmap

The development of AimSmoother is divided into the following milestones:

*   **v0.2 - The Smart App:** Focus on usability and security, with the implementation of the calibration wizard and process blacklist.
*   **v0.3 - The Control Interface:** Creation of a real-time control panel for advanced customization.
*   **v1.0 - The Polished Product:** Transform the script into a complete desktop application, with an installer, system tray icon, and startup with Windows.

## Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, feel free to open an *issue* or submit a *pull request*.

## License

This project is licensed under the [MIT License](LICENSE).