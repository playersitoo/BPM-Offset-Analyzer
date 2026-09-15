🎵 BPM & Offset Analyzer A modular audio analysis tool designed to assist osu! mappers and other rhythm game creators in accurately detecting BPM and adjusting offsets automatically.

🚀 Project Architecture The project is built using a decoupled architecture to separate analytical logic from the user interface:

Backend Engine (Python): Handles audio processing using specialized libraries like librosa and numpy to extract rhythmic features.

Graphical User Interface (C# - Planned for Beta Phase): Designed to deliver a smooth, cross-platform user experience using WPF or Avalonia, communicating with the Python engine via CLI or a local API.

📁 Repository Structure Plaintext App/ │ ├── core/ # Audio analysis logic and internationalization (i18n) │ ├── analyzer.py # Core timing and BPM calculation algorithm │ └── i18n.py # Multi-language support │ ├── ui/ # Graphical interface components │ └── app.py # Initial test views │ ├── main.py # Main entry point for the Python engine └── requirements.txt # Project dependencies ⚙️ Requirements & Installation (Alpha Phase) Ensure Python is installed on your system.

Clone the repository or download the source code.

Install the required dependencies by running the following in your terminal:

Bash pip install -r requirements.txt 🗺️ Roadmap / Next Steps [x] Base structure for the Python analysis engine.

[x] Internationalization system (multi-language support).

[ ] Refinement of transient peak detection for complex offsets.

[ ] C# GUI development for the Beta phase.

Developed for the mapping community.
