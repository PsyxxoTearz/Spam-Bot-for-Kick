from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLineEdit, QTextEdit,
                             QLabel, QListWidgetItem, QMessageBox, QTabWidget,
                             QProgressBar, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import json

class WorkerThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    
    def __init__(self, bot_manager, mode, headless=False):
        super().__init__()
        self.bot_manager = bot_manager
        self.mode = mode
        self.headless = headless
    
    def run(self):
        if self.mode == "parallel":
            results = self.bot_manager.send_messages_parallel(self.headless)
            self.finished.emit(results)
        elif self.mode == "sequential":
            results = []
            for i in range(len(self.bot_manager.accounts)):
                self.progress.emit(f"Обработка аккаунта {i+1}/{len(self.bot_manager.accounts)}")
                success, message = self.bot_manager.send_single_message(i, self.headless)
                results.append((self.bot_manager.accounts[i]["name"], success, message))
                self.msleep(2000)
            self.finished.emit(results)

class MainWindow(QMainWindow):
    def __init__(self, bot_manager):
        super().__init__()
        self.bot_manager = bot_manager
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Kick Bot Manager")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                color: white;
                padding: 8px;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #444;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
            }
        """)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        accounts_tab = QWidget()
        settings_tab = QWidget()
        send_tab = QWidget()
        
        tabs.addTab(accounts_tab, "Аккаунты")
        tabs.addTab(settings_tab, "Настройки")
        tabs.addTab(send_tab, "Отправка")
        
        self.setup_accounts_tab(accounts_tab)
        self.setup_settings_tab(settings_tab)
        self.setup_send_tab(send_tab)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)
    
    def setup_accounts_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        accounts_layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        self.accounts_list = QListWidget()
        left_panel.addWidget(QLabel("Аккаунты:"))
        left_panel.addWidget(self.accounts_list)
        
        right_panel = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя аккаунта")
        right_panel.addWidget(QLabel("Имя:"))
        right_panel.addWidget(self.name_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        right_panel.addWidget(QLabel("Пароль:"))
        right_panel.addWidget(self.password_input)
        
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("Название профиля")
        right_panel.addWidget(QLabel("Профиль:"))
        right_panel.addWidget(self.profile_input)
        
        add_btn = QPushButton("Добавить аккаунт")
        add_btn.clicked.connect(self.add_account)
        right_panel.addWidget(add_btn)
        
        remove_btn = QPushButton("Удалить выбранный")
        remove_btn.clicked.connect(self.remove_account)
        right_panel.addWidget(remove_btn)
        
        setup_btn = QPushButton("Настроить выбранный")
        setup_btn.clicked.connect(self.setup_account)
        right_panel.addWidget(setup_btn)
        
        right_panel.addStretch()
        
        accounts_layout.addLayout(left_panel, 2)
        accounts_layout.addLayout(right_panel, 1)
        
        layout.addLayout(accounts_layout)
    
    def setup_settings_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        self.streamer_input = QLineEdit()
        self.streamer_input.setPlaceholderText("Имя стримера")
        layout.addWidget(QLabel("Стример:"))
        layout.addWidget(self.streamer_input)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Сообщение для отправки")
        layout.addWidget(QLabel("Сообщение:"))
        layout.addWidget(self.message_input)
        
        save_btn = QPushButton("Сохранить настройки")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
    
    def setup_send_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        sequential_btn = QPushButton("Последовательная отправка")
        sequential_btn.clicked.connect(lambda: self.start_sending("sequential", False))
        layout.addWidget(sequential_btn)
        
        parallel_btn = QPushButton("Параллельная отправка")
        parallel_btn.clicked.connect(lambda: self.start_sending("parallel", False))
        layout.addWidget(parallel_btn)
        
        fast_btn = QPushButton("Быстрая отправка (без GUI)")
        fast_btn.clicked.connect(lambda: self.start_sending("parallel", True))
        layout.addWidget(fast_btn)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("Лог отправки:"))
        layout.addWidget(self.log_text)
    
    def load_data(self):
        for account in self.bot_manager.accounts:
            self.accounts_list.addItem(f"{account['name']} ({account['profile_dir']})")
        
        self.streamer_input.setText(self.bot_manager.config.get("streamer", ""))
        self.message_input.setPlainText(self.bot_manager.config.get("message", ""))
    
    def add_account(self):
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()
        profile = self.profile_input.text().strip()
        
        if not name or not password or not profile:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        self.bot_manager.add_account(name, password, profile)
        self.accounts_list.addItem(f"{name} ({profile})")
        
        self.name_input.clear()
        self.password_input.clear()
        self.profile_input.clear()
        
        QMessageBox.information(self, "Успех", "Аккаунт добавлен")
    
    def remove_account(self):
        current_row = self.accounts_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите аккаунт для удаления")
            return
        
        self.bot_manager.remove_account(current_row)
        self.accounts_list.takeItem(current_row)
    
    def setup_account(self):
        current_row = self.accounts_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите аккаунт для настройки")
            return
        
        QMessageBox.information(self, "Настройка", 
            "Откроется браузер. Войдите в аккаунт и закройте его после входа.")
        
        success, message = self.bot_manager.setup_account(current_row)
        
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)
    
    def save_settings(self):
        streamer = self.streamer_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not streamer or not message:
            QMessageBox.warning(self, "Ошибка", "Заполните все настройки")
            return
        
        self.bot_manager.update_config(streamer, message)
        QMessageBox.information(self, "Успех", "Настройки сохранены")
    
    def start_sending(self, mode, headless):
        if not self.bot_manager.accounts:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один аккаунт")
            return
        
        if not self.bot_manager.config.get("streamer") or not self.bot_manager.config.get("message"):
            QMessageBox.warning(self, "Ошибка", "Настройте стримера и сообщение")
            return
        
        self.progress_bar.setVisible(True)
        self.status_label.setText("Отправка сообщений...")
        
        self.worker = WorkerThread(self.bot_manager, mode, headless)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.sending_finished)
        self.worker.start()
    
    def update_progress(self, message):
        self.status_label.setText(message)
    
    def sending_finished(self, results):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Отправка завершена")
        
        log_text = "Результаты отправки:\n"
        for name, success, message in results:
            status = "✅ Успех" if success else "❌ Ошибка"
            log_text += f"{name}: {status} - {message}\n"
        
        self.log_text.setPlainText(log_text)
        
        QMessageBox.information(self, "Завершено", "Отправка сообщений завершена")