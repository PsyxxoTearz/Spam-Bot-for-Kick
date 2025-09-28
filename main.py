import sys
import os
from PyQt5.QtWidgets import QApplication
from core.bot_manager import BotManager
from ui.main_window import MainWindow

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("kick_profiles", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    bot_manager = BotManager()
    window = MainWindow(bot_manager)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()