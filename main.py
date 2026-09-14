import logging
from ui.app import BPMAnalyzerApp

if __name__ == "__main__":
    # Adiós a los 'except: pass' silenciosos. Todo se registra aquí.
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    
    logging.info("Iniciando osu! Timing Assistant - Pro Edition...")
    app = BPMAnalyzerApp()
    app.mainloop()