import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QLabel, QCheckBox,
                              QTabWidget, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

IS_WINDOWS = sys.platform == 'win32'

def get_font_family():
    if IS_WINDOWS:
        return "Segoe UI"
    elif sys.platform == 'darwin':
        return "SF Pro Display"
    else:
        return "Ubuntu"

def is_admin():
    if not IS_WINDOWS:
        return False
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class OptimizerThread(QThread):
    progress = pyqtSignal(int)
    status_text = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks

    def run(self):
        total = len(self.tasks)
        for i, (name, cmd) in enumerate(self.tasks):
            self.status_text.emit(f"Применение: {name}...")
            try:
                subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            except Exception:
                pass 
            self.progress.emit(int((i + 1) / total * 100))
        self.done.emit()


class KyzoOptimizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font_family = get_font_family()
        self.setWindowTitle("Kyzo Optimizer")
        self.setFixedSize(620, 740)
        
        # Убираем системную прозрачность окон
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #0d1117; border: none; }}
            QWidget {{ background-color: transparent; }}
            QLabel {{ color: #c9d1d9; background-color: transparent; font-family: '{self.font_family}'; }}
            QCheckBox {{ 
                color: #c9d1d9; font-size: 13px; font-family: '{self.font_family}'; 
                spacing: 12px; padding: 6px 0px; background-color: transparent; border-radius: 4px;
            }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid #30363d; border-radius: 4px; background: #0d1117; }}
            QCheckBox::indicator:checked {{ background-color: #58a6ff; border-color: #58a6ff; }}
            QCheckBox::indicator:hover {{ border-color: #58a6ff; }}
            
            QTabWidget::pane {{ border: 1px solid #21262d; background: #161b22; border-radius: 8px; top: -1px; }}
            QTabBar::tab {{ 
                background: #0d1117; color: #8b949e; padding: 10px 25px; font-size: 12px; font-weight: bold;
                font-family: '{self.font_family}';
                border: 1px solid #21262d; border-bottom: none; 
                border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; 
            }}
            QTabBar::tab:selected {{ background: #161b22; color: #58a6ff; border-bottom: 2px solid #58a6ff; }}
            QTabBar::tab:hover {{ color: #c9d1d9; background: #161b22; }}
            
            QProgressBar {{ 
                border: 1px solid #21262d; border-radius: 10px; text-align: center; 
                color: #ffffff; font-size: 11px; font-weight: bold; font-family: '{self.font_family}';
                background: #0d1117; max-height: 8px;
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #58a6ff); 
                border-radius: 10px; 
            }}
            QPushButton {{ font-family: '{self.font_family}'; }}
        """)

        if os.path.exists("kyzo.png"):
            try:
                self.setWindowIcon(QIcon("kyzo.png"))
            except:
                pass

        # Жестко задаем непрозрачный фон (фикс для Linux)
        central = QWidget()
        central.setObjectName("CentralWidget")
        central.setStyleSheet("QWidget#CentralWidget { background-color: #0d1117; }")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        self.all_checkboxes = []
        self.task_map = {}

        # --- Шапка ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Место под иконку (ровный квадрат 64x64)
        logo_label = QLabel()
        logo_label.setFixedWidth(64)
        logo_label.setFixedHeight(64)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists("kyzo.png"):
            try:
                pixmap = QPixmap("kyzo.png").scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(pixmap)
            except:
                self._set_empty_logo(logo_label)
        else:
            self._set_empty_logo(logo_label)
            
        header_layout.addWidget(logo_label)

        # Текст рядом с иконкой
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = QLabel("Kyzo Optimizer")
        title.setFont(QFont(self.font_family, 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #f0f6fc; background: transparent;")
        title_layout.addWidget(title)
        
        sub = QLabel("Мощная оптимизация и очистка Windows 11")
        sub.setFont(QFont(self.font_family, 9))
        sub.setStyleSheet("color: #484f58; background: transparent;")
        title_layout.addWidget(sub)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- Спокойное предупреждение про Defender ---
        warn_def = QFrame()
        warn_def.setStyleSheet("""
            QFrame { 
                background-color: #161b22; 
                border: none; 
                border-left: 3px solid #388bfd; 
                border-radius: 4px; 
            }
            QLabel { border: none; background-color: transparent; }
        """)
        warn_def_layout = QVBoxLayout(warn_def)
        warn_def_layout.setContentsMargins(15, 10, 15, 10)
        
        warn_def_text = QLabel("Рекомендация: перед запуском оптимизации временно отключите Защитник Windows (Defender), чтобы избежать блокировки системных скриптов.")
        warn_def_text.setFont(QFont(self.font_family, 9))
        warn_def_text.setStyleSheet("color: #8b949e;")
        warn_def_text.setWordWrap(True)
        warn_def_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_def_layout.addWidget(warn_def_text)
        main_layout.addWidget(warn_def)

        # --- Проверка админа (ТОЛЬКО для Windows) ---
        if IS_WINDOWS and not is_admin():
            warn_admin = QFrame()
            warn_admin.setStyleSheet("""
                QFrame { background-color: #161b22; border: none; border-left: 3px solid #d29922; border-radius: 4px; }
                QLabel { color: #d29922; border: none; background-color: transparent; }
            """)
            warn_admin_lay = QVBoxLayout(warn_admin)
            warn_admin_lay.setContentsMargins(15, 10, 15, 10)
            warn_admin_text = QLabel("Программа запущена без прав Администратора. Изменения не вступят в силу.")
            warn_admin_text.setFont(QFont(self.font_family, 9))
            warn_admin_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warn_admin_lay.addWidget(warn_admin_text)
            main_layout.addWidget(warn_admin)

        # --- Вкладки ---
        self.tabs = QTabWidget()
        self.tab_privacy = QWidget()
        self.tab_gaming = QWidget()
        self.tab_ui = QWidget()
        self.tab_bloat = QWidget()

        self.tabs.addTab(self.tab_privacy, " Конфиденциальность ")
        self.tabs.addTab(self.tab_gaming, " Игры ")
        self.tabs.addTab(self.tab_ui, " Интерфейс ")
        self.tabs.addTab(self.tab_bloat, " Мусор ")

        self.setup_privacy_tab()
        self.setup_gaming_tab()
        self.setup_ui_tab()
        self.setup_bloat_tab()

        main_layout.addWidget(self.tabs)

        # --- Кнопки управления чекбоксами ---
        cb_ctrl_layout = QHBoxLayout()
        btn_sel_all = QPushButton("Выбрать всё")
        btn_desel_all = QPushButton("Сбросить")
        for btn in [btn_sel_all, btn_desel_all]:
            btn.setFixedHeight(28)
            btn.setFont(QFont(self.font_family, 9))
            btn.setStyleSheet("""
                QPushButton { color: #8b949e; background: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 0 15px; }
                QPushButton:hover { color: #c9d1d9; border-color: #8b949e; }
            """)
        btn_sel_all.clicked.connect(lambda: [cb.setChecked(True) for cb in self.all_checkboxes])
        btn_desel_all.clicked.connect(lambda: [cb.setChecked(False) for cb in self.all_checkboxes])
        cb_ctrl_layout.addStretch()
        cb_ctrl_layout.addWidget(btn_sel_all)
        cb_ctrl_layout.addWidget(btn_desel_all)
        main_layout.addLayout(cb_ctrl_layout)

        # --- Прогресс ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("")
        main_layout.addWidget(self.progress)

        # --- Статус ---
        self.status = QLabel("Ожидание действий...")
        self.status.setFont(QFont(self.font_family, 9))
        self.status.setStyleSheet("color: #58a6ff; background: transparent;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status)

        # --- Кнопки действий ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.run_btn = QPushButton("Запустить оптимизацию")
        self.run_btn.setFixedHeight(45)
        self.run_btn.setFont(QFont(self.font_family, 11, QFont.Weight.Bold))
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #238636, stop:1 #2ea043);
                color: white; border: none; border-radius: 8px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ea043, stop:1 #3fb950); }
            QPushButton:pressed { background: #238636; }
            QPushButton:disabled { background: #21262d; color: #484f58; }
        """)
        self.run_btn.clicked.connect(self.run_optimizer)
        btn_layout.addWidget(self.run_btn)

        self.restore_btn = QPushButton("Восстановить всё")
        self.restore_btn.setFixedHeight(45)
        self.restore_btn.setFont(QFont(self.font_family, 11, QFont.Weight.Bold))
        self.restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px;
            }
            QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
            QPushButton:pressed { background: #21262d; }
            QPushButton:disabled { background-color: #161b22; color: #484f58; border: 1px solid #21262d; }
        """)
        self.restore_btn.clicked.connect(self.restore_all)
        btn_layout.addWidget(self.restore_btn)

        main_layout.addLayout(btn_layout)

        # --- Подвал ---
        bottom = QLabel("Kyzo Optimizer v2.0 Premium")
        bottom.setFont(QFont(self.font_family, 8))
        bottom.setStyleSheet("color: #30363d; background: transparent;")
        bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(bottom)

        if IS_WINDOWS and not is_admin():
            self.run_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)

        self.thread = None

    def _set_empty_logo(self, label):
        """Создает аккуратную заглушку, если нет картинки kyzo.png"""
        label.setText("KYZO")
        label.setFont(QFont(self.font_family, 10, QFont.Weight.Bold))
        label.setStyleSheet("""
            QLabel { 
                color: #21262d; 
                background-color: #161b22; 
                border: 1px dashed #30363d; 
                border-radius: 8px; 
            }
        """)

    def make_checkbox(self, text, parent_layout, index):
        cb = QCheckBox(text)
        cb.setChecked(True)
        parent_layout.addWidget(cb)
        self.all_checkboxes.append(cb)
        return cb

    def add_task(self, index, name, apply_cmd, restore_cmd):
        self.task_map[index] = (name, apply_cmd, restore_cmd)

    def setup_privacy_tab(self):
        layout = QVBoxLayout(self.tab_privacy)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        idx = 0
        self.make_checkbox("Отключить телеметрию и сбор диагностических данных", layout, idx)
        self.add_task(idx, "Телеметрия", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f', 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 3 /f')
        idx += 1
        self.make_checkbox("Отключить Windows Copilot", layout, idx)
        self.add_task(idx, "Copilot", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f', 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsCopilot" /v TurnOffWindowsCopilot /f')
        idx += 1
        self.make_checkbox("Отключить Кортану и веб-поиск в меню Пуск", layout, idx)
        self.add_task(idx, "Кортана", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f', 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /f')
        idx += 1
        self.make_checkbox("Отключить рекламный идентификатор", layout, idx)
        self.add_task(idx, "Рекламный ID", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AdvertisingInfo" /v DisabledByGroupPolicy /t REG_DWORD /d 1 /f', 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AdvertisingInfo" /v DisabledByGroupPolicy /t REG_DWORD /d 0 /f')
        idx += 1
        self.make_checkbox("Отключить историю действий (Timeline)", layout, idx)
        self.add_task(idx, "История действий", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f', 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 1 /f')
        layout.addStretch()

    def setup_gaming_tab(self):
        layout = QVBoxLayout(self.tab_gaming)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        idx = 5
        self.make_checkbox("Отключить Xbox Game Bar", layout, idx)
        self.add_task(idx, "Xbox Game Bar", 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f', 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 1 /f')
        idx += 1
        self.make_checkbox("Удалить встроенные приложения Xbox", layout, idx)
        self.add_task(idx, "Удаление Xbox", 'powershell -Command "Get-AppxPackage *xbox* | Remove-AppxPackage"', 'powershell -Command "Get-AppxPackage -AllUsers *xbox* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}"')
        idx += 1
        self.make_checkbox("Отключить фоновую запись игр (Game DVR)", layout, idx)
        self.add_task(idx, "Game DVR", 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v GameDVR_Enabled /t REG_DWORD /d 0 /f', 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v GameDVR_Enabled /t REG_DWORD /d 1 /f')
        layout.addStretch()

    def setup_ui_tab(self):
        layout = QVBoxLayout(self.tab_ui)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        idx = 8
        self.make_checkbox("Отключить прозрачность и эффекты окна", layout, idx)
        self.add_task(idx, "Прозрачность", 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f', 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 1 /f')
        idx += 1
        self.make_checkbox("Отключить анимации окон и элементов", layout, idx)
        self.add_task(idx, "Анимации", 'reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_DWORD /d 0 /f', 'reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_DWORD /d 1 /f')
        idx += 1
        self.make_checkbox("Убрать виджеты с панели задач", layout, idx)
        self.add_task(idx, "Виджеты", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f', 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v AllowNewsAndInterests /f')
        idx += 1
        self.make_checkbox("Отключить всплывающие уведомления", layout, idx)
        self.add_task(idx, "Уведомления", 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f', 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 1 /f')
        idx += 1
        self.make_checkbox("Скрыть ленту новостей (Chat/Microsoft Teams)", layout, idx)
        self.add_task(idx, "Новости", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Feeds" /v EnableFeeds /t REG_DWORD /d 0 /f', 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Feeds" /v EnableFeeds /f')
        layout.addStretch()

    def setup_bloat_tab(self):
        layout = QVBoxLayout(self.tab_bloat)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        idx = 13
        self.make_checkbox("Отключить автозапуск OneDrive", layout, idx)
        self.add_task(idx, "OneDrive", 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f', 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 0 /f')
        idx += 1
        self.make_checkbox("Удалить Skype", layout, idx)
        self.add_task(idx, "Skype", 'powershell -Command "Get-AppxPackage *skype* | Remove-AppxPackage"', 'powershell -Command "Get-AppxPackage -AllUsers *skype* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}"')
        idx += 1
        self.make_checkbox("Удалить OneNote", layout, idx)
        self.add_task(idx, "OneNote", 'powershell -Command "Get-AppxPackage *onenote* | Remove-AppxPackage"', 'powershell -Command "Get-AppxPackage -AllUsers *onenote* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}"')
        idx += 1
        self.make_checkbox("Удалить приложения Bing (Погода, Новости и т.д.)", layout, idx)
        self.add_task(idx, "Bing", 'powershell -Command "Get-AppxPackage *bing* | Remove-AppxPackage"', 'powershell -Command "Get-AppxPackage -AllUsers *bing* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}"')
        idx += 1
        self.make_checkbox("Удалить Candy Crush и прочий мусорный софт", layout, idx)
        self.add_task(idx, "Candy Crush", 'powershell -Command "Get-AppxPackage *candy* | Remove-AppxPackage; Get-AppxPackage *king* | Remove-AppxPackage; Get-AppxPackage *farm* | Remove-AppxPackage"', 'powershell -Command "Get-AppxPackage -AllUsers *king* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}"')
        layout.addStretch()

    def get_selected_tasks(self, mode="apply"):
        tasks = []
        for idx, cb in enumerate(self.all_checkboxes):
            if cb.isChecked() and idx in self.task_map:
                name, apply_cmd, restore_cmd = self.task_map[idx]
                cmd = apply_cmd if mode == "apply" else restore_cmd
                tasks.append((name, cmd))
        return tasks

    def run_optimizer(self):
        tasks = self.get_selected_tasks("apply")
        if not tasks:
            self.status.setText("Выберите хотя бы один пункт для оптимизации.")
            self.status.setStyleSheet("color: #f0883e; background: transparent;")
            return
        self.status.setStyleSheet("color: #58a6ff; background: transparent;")
        self.start_thread(tasks, "Оптимизация")

    def restore_all(self):
        tasks = []
        for idx in self.task_map:
            name, apply_cmd, restore_cmd = self.task_map[idx]
            tasks.append((name, restore_cmd))
        self.start_thread(tasks, "Восстановление")

    def start_thread(self, tasks, action_name):
        self.run_btn.setEnabled(False)
        self.restore_btn.setEnabled(False)
        self.tabs.setEnabled(False)
        self.progress.setValue(0)
        self.status.setText(f"{action_name}...")
        self.thread = OptimizerThread(tasks)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.status_text.connect(self.status.setText)
        self.thread.done.connect(self.on_done)
        self.thread.start()

    def on_done(self):
        self.run_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.tabs.setEnabled(True)
        self.progress.setValue(100)
        
        if not IS_WINDOWS:
            self.status.setText("Симуляция завершена.")
        else:
            self.status.setText("Выполнено успешно. Рекомендуется перезагрузить ПК.")
            
        self.status.setStyleSheet("color: #3fb950; background: transparent;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    font = QFont(get_font_family(), 9)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)
    
    window = KyzoOptimizer()
    window.show()
    sys.exit(app.exec())
