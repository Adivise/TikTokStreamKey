import glob
import os
import platform
import re
import sys
import json
import threading
import traceback
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QGroupBox, QPushButton, QLineEdit, QLabel, QCheckBox,
                              QListWidget, QMessageBox, QListWidgetItem, QSizePolicy,
                              QProgressBar, QFrame)
from PySide6.QtCore import Signal, QTimer, Qt, QSize
from PySide6.QtGui import QDesktopServices, QFont, QColor, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import QStyle
from stream_client import Stream

class StreamApp(QMainWindow):
    update_suggestions = Signal(list)
    update_ui = Signal()
    token_loaded = Signal(str)
    show_message = Signal(str, str, str)  # title, message, type (info/error/success)
    update_loading = Signal(bool)
    enable_button = Signal(str, bool)  # button_name, enabled
    set_button_text = Signal(str, str)  # button_name, text
    set_stream_info = Signal(str, str)  # url, key
    clear_stream_info = Signal()
    
    def __init__(self):
        super().__init__()
        self.stream = None
        self.game_mask_id = ""
        self.token_visible_timeout = None
        self.is_loading = False
        self.suppress_donation_reminder = False
        
        # Cache icons to avoid repeated creation
        self._icon_cache = {}
        
        # Connect signals first for faster UI responsiveness
        self.update_suggestions.connect(self.update_suggestions_list)
        self.update_ui.connect(self.handle_ui_update)
        self.token_loaded.connect(self.handle_token_loaded)
        self.show_message.connect(self.handle_show_message)
        self.update_loading.connect(self.handle_update_loading)
        self.enable_button.connect(self.handle_enable_button)
        self.set_button_text.connect(self.handle_set_button_text)
        self.set_stream_info.connect(self.handle_set_stream_info)
        self.clear_stream_info.connect(self.handle_clear_stream_info)
        
        # Initialize UI
        self.init_ui()
        self.apply_modern_styles()
        
        # Defer icon loading to improve startup time
        QTimer.singleShot(0, self.set_app_icon)
        
        # Load config after UI is ready
        QTimer.singleShot(0, self.load_config)
        
        # Defer non-critical startup operations
        QTimer.singleShot(3000, lambda: [
            self.show_donation_reminder(),
            QTimer.singleShot(3000, self.check_updates_on_startup)
        ])
    
    def create_icon_from_text(self, text, size=20):
        """Create an icon from text/emoji (cached)"""
        cache_key = f"{text}_{size}"
        if cache_key not in self._icon_cache:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            font = QFont()
            font.setPixelSize(size - 4)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
            painter.end()
            self._icon_cache[cache_key] = QIcon(pixmap)
        return self._icon_cache[cache_key]
    
    def get_eye_icon(self):
        """Get eye icon for show/hide token (cached)"""
        if "eye" not in self._icon_cache:
            self._icon_cache["eye"] = self.create_icon_from_text("👁", 20)
        return self._icon_cache["eye"]
    
    def get_lock_icon(self):
        """Get lock icon for hide token (cached)"""
        if "lock" not in self._icon_cache:
            self._icon_cache["lock"] = self.create_icon_from_text("🔒", 20)
        return self._icon_cache["lock"]
    
    def get_clear_icon(self):
        """Get clear/close icon (cached)"""
        if "clear" not in self._icon_cache:
            # Try to use built-in close icon, fallback to X emoji
            style = self.style()
            if style:
                icon = style.standardIcon(QStyle.SP_DialogCloseButton)
                if not icon.isNull():
                    self._icon_cache["clear"] = icon
                    return icon
            # Fallback to emoji X
            self._icon_cache["clear"] = self.create_icon_from_text("✖", 18)
        return self._icon_cache["clear"]
    
    @staticmethod
    def get_app_icon():
        """Get the application icon (static method to use before window creation)"""
        # Try to load from file first
        icon_paths = [
            "streamkey.ico",
            "streamkey.png",
            "app_icon.png",
            "icon.ico"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    return icon
        
        # Fallback: Create icon from emoji/symbol
        return StreamApp.create_app_icon_fallback_static()
    
    @staticmethod
    def create_app_icon_fallback_static():
        """Create a high-quality app icon as fallback (static version)"""
        # Create multiple sizes for better icon quality
        icon = QIcon()
        sizes = [16, 32, 48, 64, 128, 256]
        
        for size in sizes:
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(26, 30, 46))  # Dark background matching theme
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw a rounded rectangle background
            painter.setBrush(QColor(74, 158, 255))  # Blue accent color
            painter.setPen(Qt.NoPen)
            rect = pixmap.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 8, 8)
            
            # Draw emoji/text on top
            font = QFont()
            font.setPixelSize(int(size * 0.6))
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "🎬")
            painter.end()
            
            icon.addPixmap(pixmap)
        
        return icon
    
    def set_app_icon(self):
        """Set the application window icon"""
        icon = StreamApp.get_app_icon()
        self.setWindowIcon(icon)
        # Also ensure it's set on the application
        QApplication.setWindowIcon(icon)
    
    
    def apply_modern_styles(self):
        """Apply modern, responsive styling to the application (cached)"""
        # Stylesheet is only applied once, so caching isn't necessary here
        # But we keep it as a method for maintainability
        stylesheet = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #252525;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a9eff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                color: #e0e0e0;
                selection-background-color: #4a9eff;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: #333333;
            }
            QLineEdit:disabled {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                color: #666666;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                color: #ffffff;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 2px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #252525;
                border: 2px solid #2a2a2a;
                color: #666666;
            }
            QPushButton#go_live_btn {
                background-color: #00d4aa;
                border: 2px solid #00b894;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton#go_live_btn:hover:enabled {
                background-color: #00e6b8;
                border: 2px solid #00d4aa;
            }
            QPushButton#end_live_btn {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton#end_live_btn:hover:enabled {
                background-color: #ff5a4a;
                border: 2px solid #e74c3c;
            }
            QPushButton#copy_btn {
                background-color: #4a9eff;
                border: 2px solid #3a8eef;
            }
            QPushButton#copy_btn:hover:enabled {
                background-color: #5aaeff;
                border: 2px solid #4a9eff;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 4px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #4a9eff;
                color: #ffffff;
            }
            QCheckBox {
                font-size: 12px;
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4a4a4a;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #5a5a5a;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border: 2px solid #3a8eef;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QLabel[status="success"] {
                color: #00d4aa;
            }
            QLabel[status="error"] {
                color: #e74c3c;
            }
            QLabel[status="warning"] {
                color: #f39c12;
            }
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                text-align: center;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        self.setWindowTitle("TikTok StreamKey | Generator")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Left column
        left_column = QVBoxLayout()
        main_layout.addLayout(left_column)

        # Token Section
        token_group = QGroupBox("🔐 Token Loader")
        token_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        left_column.addWidget(token_group)

        token_layout = QVBoxLayout()
        token_layout.setContentsMargins(12, 16, 12, 12)
        token_layout.setSpacing(8)
        token_group.setLayout(token_layout)

        # Token Entry Row
        token_entry_row = QHBoxLayout()
        token_entry_row.setSpacing(8)

        self.token_entry = QLineEdit()
        self.token_entry.setPlaceholderText("Paste token here or load below...")
        self.token_entry.setEchoMode(QLineEdit.Password)
        self.token_entry.setFixedHeight(36)
        self.token_entry.textChanged.connect(self.handle_token_change)
        self.token_entry.returnPressed.connect(self.refresh_account_info)
        token_entry_row.addWidget(self.token_entry)

        # Eye icon for password visibility
        self.toggle_token_btn = QPushButton()
        self.toggle_token_btn.setFixedSize(36, 36)
        self.toggle_token_btn.setIcon(self.get_eye_icon())
        self.toggle_token_btn.setIconSize(QSize(20, 20))
        self.toggle_token_btn.setToolTip("Show token (auto-hides after 10 seconds)")
        self.toggle_token_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 2px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        self.toggle_token_btn.clicked.connect(self.toggle_token_visibility)
        token_entry_row.addWidget(self.toggle_token_btn)
        
        # Clear token button for security
        self.clear_token_btn = QPushButton()
        self.clear_token_btn.setFixedSize(36, 36)
        self.clear_token_btn.setIcon(self.get_clear_icon())
        self.clear_token_btn.setIconSize(QSize(18, 18))
        self.clear_token_btn.setToolTip("Clear token (for security)")
        self.clear_token_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #4a3a3a;
                border: 2px solid #e74c3c;
            }
            QPushButton:pressed {
                background-color: #2a1a1a;
            }
        """)
        self.clear_token_btn.clicked.connect(self.clear_token)
        token_entry_row.addWidget(self.clear_token_btn)

        token_layout.addLayout(token_entry_row)
        
        # Security warning label
        self.token_warning_label = QLabel("⚠️ Token is visible - will auto-hide in 10 seconds")
        self.token_warning_label.setStyleSheet("color: #f39c12; font-size: 10px; padding: 4px;")
        self.token_warning_label.hide()
        token_layout.addWidget(self.token_warning_label)

        # Token Load Buttons Row
        load_buttons_row = QHBoxLayout()
        load_buttons_row.setSpacing(8)

        # Local Token Button
        self.load_local_btn = QPushButton("💾 Load from PC")
        self.load_local_btn.setFixedHeight(36)
        self.load_local_btn.setToolTip("Load token from Streamlabs desktop app data")
        self.load_local_btn.clicked.connect(self.load_local_token)
        load_buttons_row.addWidget(self.load_local_btn)

        # Online Token Button
        self.load_online_btn = QPushButton("🌐 Load from Web")
        self.load_online_btn.setFixedHeight(36)
        self.load_online_btn.setToolTip("Get token through browser login")
        self.load_online_btn.clicked.connect(self.fetch_online_token)
        load_buttons_row.addWidget(self.load_online_btn)

        token_layout.addLayout(load_buttons_row)
        
        # Loading indicator
        self.loading_progress = QProgressBar()
        self.loading_progress.setFixedHeight(4)
        self.loading_progress.setRange(0, 0)  # Indeterminate
        self.loading_progress.hide()
        token_layout.addWidget(self.loading_progress)

        # Binary Location Input Row
        if platform.system() == "Linux":
            binary_row = QHBoxLayout()
            binary_row.setSpacing(8)

            self.binary_location_entry = QLineEdit()
            self.binary_location_entry.setPlaceholderText("Custom Chrome binary path (optional)")
            self.binary_location_entry.setFixedHeight(36)
            self.binary_location_entry.setToolTip("Leave empty to auto-detect Chrome path on Linux")
            binary_row.addWidget(self.binary_location_entry)
            
            token_layout.addLayout(binary_row)


        # Account Info Section
        account_info_label = QLabel("👤 Account Information")
        account_info_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 12px; color: #4a9eff;")
        token_layout.addWidget(account_info_label)

        # Username
        username_row = QHBoxLayout()
        username_row.setSpacing(8)
        username_label = QLabel("Username:")
        username_label.setFixedWidth(110)
        self.tiktok_username = QLineEdit()
        self.tiktok_username.setReadOnly(True)
        self.tiktok_username.setFixedHeight(32)
        username_row.addWidget(username_label)
        username_row.addWidget(self.tiktok_username)
        token_layout.addLayout(username_row)

        # Status
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_label = QLabel("Status:")
        status_label.setFixedWidth(110)
        self.app_status = QLineEdit()
        self.app_status.setReadOnly(True)
        self.app_status.setFixedHeight(32)
        status_row.addWidget(status_label)
        status_row.addWidget(self.app_status)
        token_layout.addLayout(status_row)

        # Go Live Status with visual indicator
        live_row = QHBoxLayout()
        live_row.setSpacing(8)
        live_label = QLabel("Can Go Live:")
        live_label.setFixedWidth(110)
        self.can_go_live = QLineEdit()
        self.can_go_live.setReadOnly(True)
        self.can_go_live.setFixedHeight(32)
        # Status indicator dot
        self.live_status_indicator = QLabel("●")
        self.live_status_indicator.setFixedSize(16, 16)
        self.live_status_indicator.setStyleSheet("color: #666666; font-size: 16px;")
        live_row.addWidget(live_label)
        live_row.addWidget(self.can_go_live)
        live_row.addWidget(self.live_status_indicator)
        token_layout.addLayout(live_row)
        
        # Refresh account info button
        refresh_btn = QPushButton("🔄 Refresh Account Info")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setToolTip("Refresh account information")
        refresh_btn.clicked.connect(self.refresh_account_info)
        token_layout.addWidget(refresh_btn)

        # Add stretch to prevent expansion
        token_layout.addStretch()

        # Stream Details
        stream_group = QGroupBox("📺 Stream Details")
        stream_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        left_column.addWidget(stream_group)
        stream_layout = QVBoxLayout()
        stream_layout.setContentsMargins(12, 16, 12, 12)
        stream_layout.setSpacing(10)
        stream_group.setLayout(stream_layout)

        # Stream Title
        title_label = QLabel("Stream Title:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #4a9eff;")
        stream_layout.addWidget(title_label)
        self.stream_title = QLineEdit()
        self.stream_title.setFixedHeight(36)
        self.stream_title.setPlaceholderText("Enter your stream title...")
        stream_layout.addWidget(self.stream_title)

        # Game Category
        game_label = QLabel("Game Category:")
        game_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #4a9eff;")
        stream_layout.addWidget(game_label)
        self.game_category = QLineEdit()
        self.game_category.setFixedHeight(36)
        self.game_category.setPlaceholderText("Search for a game category...")
        self.game_category.textChanged.connect(self.handle_game_search)
        stream_layout.addWidget(self.game_category)

        # Suggestions List
        self.suggestions_list = QListWidget()
        self.suggestions_list.hide()
        self.suggestions_list.setFixedHeight(120)
        self.suggestions_list.itemClicked.connect(self.handle_suggestion_selected)
        stream_layout.addWidget(self.suggestions_list)

        # Mature Checkbox
        self.mature_checkbox = QCheckBox("🔞 Enable mature content")
        self.mature_checkbox.setStyleSheet("padding: 4px;")
        stream_layout.addWidget(self.mature_checkbox)

        # Add stretch to push everything up
        stream_layout.addStretch()

        # Right column (Controls)
        control_group = QGroupBox("🎮 Stream Control")
        control_group.setMinimumWidth(280)
        control_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        main_layout.addWidget(control_group)

        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(12, 16, 12, 12)
        control_layout.setSpacing(12)
        control_group.setLayout(control_layout)

        # Buttons row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.go_live_btn = QPushButton("▶️ Go Live")
        self.go_live_btn.setObjectName("go_live_btn")
        self.go_live_btn.setEnabled(False)
        self.go_live_btn.clicked.connect(self.start_stream)
        self.go_live_btn.setFixedHeight(42)
        button_row.addWidget(self.go_live_btn)

        self.end_live_btn = QPushButton("⏹️ End Live")
        self.end_live_btn.setObjectName("end_live_btn")
        self.end_live_btn.setEnabled(False)
        self.end_live_btn.clicked.connect(self.end_stream)
        self.end_live_btn.setFixedHeight(42)
        button_row.addWidget(self.end_live_btn)

        control_layout.addLayout(button_row)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #3a3a3a;")
        control_layout.addWidget(separator)

        # URL Section
        url_label = QLabel("🔗 Stream URL:")
        url_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #4a9eff; margin-top: 8px;")
        control_layout.addWidget(url_label)

        self.stream_url = QLineEdit()
        self.stream_url.setReadOnly(True)
        self.stream_url.setFixedHeight(36)
        self.stream_url.setPlaceholderText("Stream URL will appear here...")
        control_layout.addWidget(self.stream_url)

        self.copy_url_btn = QPushButton("📋 Copy URL")
        self.copy_url_btn.setObjectName("copy_btn")
        self.copy_url_btn.setFixedHeight(36)
        self.copy_url_btn.clicked.connect(lambda: self.copy_to_clipboard(self.stream_url))
        control_layout.addWidget(self.copy_url_btn)

        # Key Section
        key_label = QLabel("🔑 Stream Key:")
        key_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #4a9eff; margin-top: 8px;")
        control_layout.addWidget(key_label)

        self.stream_key = QLineEdit()
        self.stream_key.setReadOnly(True)
        self.stream_key.setFixedHeight(36)
        self.stream_key.setEchoMode(QLineEdit.Password)
        self.stream_key.setPlaceholderText("Stream key will appear here...")
        control_layout.addWidget(self.stream_key)

        self.copy_key_btn = QPushButton("📋 Copy Key")
        self.copy_key_btn.setObjectName("copy_btn")
        self.copy_key_btn.setFixedHeight(36)
        self.copy_key_btn.clicked.connect(lambda: self.copy_to_clipboard(self.stream_key))
        control_layout.addWidget(self.copy_key_btn)

        # Add stretch to prevent expansion of widgets
        control_layout.addStretch()
        
        # Bottom buttons
        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(8)
        left_column.addLayout(bottom_buttons)

        self.save_btn = QPushButton("💾 Save Config")
        self.save_btn.setFixedHeight(36)
        self.save_btn.clicked.connect(lambda: self.save_config())
        bottom_buttons.addWidget(self.save_btn)

        self.help_btn = QPushButton("❓ Help")
        self.help_btn.setFixedHeight(36)
        self.help_btn.clicked.connect(self.show_help)
        bottom_buttons.addWidget(self.help_btn)
        
        self.donate_btn = QPushButton("☕ Donate")
        self.donate_btn.setFixedHeight(36)
        self.donate_btn.setToolTip("Support the developer")
        self.donate_btn.clicked.connect(lambda: QDesktopServices.openUrl("https://buymeacoffee.com/loukious"))
        bottom_buttons.addWidget(self.donate_btn)

        self.monitor_btn = QPushButton("📊 Live Monitor")
        self.monitor_btn.setFixedHeight(36)
        self.monitor_btn.clicked.connect(self.open_live_monitor)
        bottom_buttons.addWidget(self.monitor_btn)

    def toggle_token_visibility(self):
        """Toggle token visibility with auto-hide security feature"""
        if self.token_entry.echoMode() == QLineEdit.Normal:
            # Hide token
            self.token_entry.setEchoMode(QLineEdit.Password)
            self.toggle_token_btn.setIcon(self.get_eye_icon())
            self.toggle_token_btn.setToolTip("Show token (auto-hides after 10 seconds)")
            self.token_warning_label.hide()
            if self.token_visible_timeout:
                self.token_visible_timeout.stop()
        else:
            # Show token with auto-hide
            self.token_entry.setEchoMode(QLineEdit.Normal)
            self.toggle_token_btn.setIcon(self.get_lock_icon())
            self.toggle_token_btn.setToolTip("Hide token")
            self.token_warning_label.show()
            
            # Auto-hide after 10 seconds for security
            if self.token_visible_timeout:
                self.token_visible_timeout.stop()
            self.token_visible_timeout = QTimer()
            self.token_visible_timeout.setSingleShot(True)
            self.token_visible_timeout.timeout.connect(lambda: [
                self.token_entry.setEchoMode(QLineEdit.Password),
                self.toggle_token_btn.setIcon(self.get_eye_icon()),
                self.toggle_token_btn.setToolTip("Show token (auto-hides after 10 seconds)"),
                self.token_warning_label.hide()
            ])
            self.token_visible_timeout.start(10000)  # 10 seconds
    
    def clear_token(self):
        """Clear token for security"""
        reply = QMessageBox.question(
            self, 
            "Clear Token", 
            "Are you sure you want to clear the token? This will require you to reload it.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.token_entry.clear()
            self.stream = None
            self.tiktok_username.clear()
            self.app_status.clear()
            self.can_go_live.clear()
            self.live_status_indicator.setStyleSheet("color: #666666; font-size: 16px;")
            self.go_live_btn.setEnabled(False)
            self.stream_title.setEnabled(False)
            self.game_category.setEnabled(False)
            self.mature_checkbox.setEnabled(False)

    def handle_token_change(self):
        self.go_live_btn.setEnabled(bool(self.token_entry.text()))

    def load_config(self):
        try:
            with open("config.json", "r") as file:
                data = json.load(file)
        except:
            data = {}
        self.token_entry.setText(data.get("token", ""))
        self.stream_title.setText(data.get("title", ""))
        self.game_category.setText(data.get("game", ""))
        self.mature_checkbox.setChecked(data.get("audience_type", "0") == "1")
        self.suppress_donation_reminder = data.get("suppress_donation_reminder", False)

        self.refresh_account_info()

    def save_config(self, show_message=True):
        try:
            data = {
                "title": self.stream_title.text(),
                "game": self.game_category.text(),
                "audience_type": "1" if self.mature_checkbox.isChecked() else "0",
                "token": self.token_entry.text(),
                "suppress_donation_reminder": self.suppress_donation_reminder
            }
            with open("config.json", "w") as file:
                json.dump(data, file, indent=2)
            if show_message:
                self.save_btn.setText("✅ Saved!")
                QTimer.singleShot(2000, lambda: self.save_btn.setText("💾 Save Config"))
                QMessageBox.information(self, "✅ Config Saved", "Configuration saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to save configuration: {str(e)}")

    def load_account_info(self):
        if not self.stream:
            self.loading_progress.hide()
            return
            
        try:
            self.loading_progress.show()
            info = self.stream.getInfo()
            user = info.get("user", {})
            self.tiktok_username.setText(user.get("username", "Unknown"))
            
            app_status = info.get("application_status", {})
            status_text = app_status.get("status", "Unknown")
            self.app_status.setText(status_text)
            
            can_go_live = info.get("can_be_live", False)
            self.can_go_live.setText(str(can_go_live))
            
            # Update live status indicator - cache stylesheet strings
            if can_go_live:
                self.live_status_indicator.setStyleSheet("color: #00d4aa; font-size: 16px;")
                self.can_go_live.setStyleSheet("color: #00d4aa;")
            else:
                self.live_status_indicator.setStyleSheet("color: #e74c3c; font-size: 16px;")
                self.can_go_live.setStyleSheet("color: #e74c3c;")
            
            # Batch UI updates
            enabled = can_go_live and bool(self.token_entry.text())
            self.stream_title.setEnabled(can_go_live)
            self.game_category.setEnabled(can_go_live)
            self.mature_checkbox.setEnabled(can_go_live)
            self.go_live_btn.setEnabled(enabled)
            
            self.loading_progress.hide()

        except Exception as e:
            self.loading_progress.hide()
            self.live_status_indicator.setStyleSheet("color: #e74c3c; font-size: 16px;")
            QMessageBox.critical(self, "Error", f"Failed to load account info: {str(e)}")
    
    def refresh_account_info(self):
        token = self.token_entry.text()
        if token:
            # Reuse Stream object if token hasn't changed
            if self.stream is None or not hasattr(self.stream, 's') or \
               self.stream.s.headers.get('authorization') != f"Bearer {token}":
                self.stream = Stream(token)
            self.load_account_info()
            self.fetch_game_mask_id(self.game_category.text())
        self.save_config(False)

    def load_local_token(self):
        self.enable_button.emit("load_local", False)
        self.update_loading.emit(True)
        
        def load_token_thread():
            try:
                # Determine the correct path based on the operating system
                if platform.system() == 'Windows':
                    path_pattern = os.path.expandvars(r'%appdata%\slobs-client\Local Storage\leveldb\*.log')
                elif platform.system() == 'Darwin':  # macOS
                    path_pattern = os.path.expanduser('~/Library/Application Support/slobs-client/Local Storage/leveldb/*.log')
                else:
                    self.show_message.emit("Error", "Unsupported operating system for local token retrieval.", "error")
                    self.enable_button.emit("load_local", True)
                    self.update_loading.emit(False)
                    return

                # Get all files matching the pattern
                files = glob.glob(path_pattern)
                
                if not files:
                    self.show_message.emit("Error", "No Streamlabs log files found. Make sure Streamlabs is installed and you're logged in using TikTok.", "error")
                    self.enable_button.emit("load_local", True)
                    self.update_loading.emit(False)
                    return
                
                # Sort files by date modified, newest first (most likely to have current token)
                files.sort(key=os.path.getmtime, reverse=True)
                
                # Compile regex pattern once (cached for performance)
                token_pattern = re.compile(r'"apiToken":"([a-f0-9]+)"', re.IGNORECASE)
                
                token = None
                
                # Loop through files and search for the token pattern
                # Limit to first 10 files for performance (newest files are checked first)
                for file in files[:10]:
                    try:
                        # Use binary mode and decode for better performance on large files
                        with open(file, 'rb') as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            matches = token_pattern.findall(content)
                            if matches:
                                # Get the last occurrence of the token (most recent)
                                token = matches[-1]
                                break
                    except (IOError, OSError, UnicodeDecodeError):
                        continue  # Silently continue to next file
                
                if token:
                    self.token_loaded.emit(token)
                    self.show_message.emit("Success", "Token loaded successfully!", "success")
                else:
                    self.show_message.emit("Error", "No API Token found locally. Make sure Streamlabs is installed and you're logged in using TikTok.", "error")
            except Exception as e:
                self.show_message.emit("Error", f"Failed to load token: {str(e)}", "error")
            finally:
                self.enable_button.emit("load_local", True)
                self.update_loading.emit(False)
        
        threading.Thread(target=load_token_thread, daemon=True).start()


    def fetch_online_token(self):
        self.enable_button.emit("load_online", False)
        self.update_loading.emit(True)
        
        def fetch_token_thread():
            try:
                # Lazy import TokenRetriever - only load when needed (heavy seleniumbase dependency)
                from token_retriever import TokenRetriever
                retriever = TokenRetriever()
                binary_path = None
                if hasattr(self, "binary_location_entry"):
                    binary_path = self.binary_location_entry.text().strip() or None
                token = retriever.retrieve_token(binary_path)
                
                if token:
                    self.token_loaded.emit(token)
                    self.show_message.emit("Success", "Token retrieved successfully!", "success")
                else:
                    self.show_message.emit("Error", "Failed to obtain token online!", "error")
            except Exception as e:
                if "Chrome not found" in str(e):
                    self.show_message.emit("Error", "Google Chrome not found. Please install it to use this feature.", "error")
                else:
                    self.show_message.emit("Error", f"Unexpected error: {e}", "error")
                print(traceback.format_exc())
            finally:
                self.enable_button.emit("load_online", True)
                self.update_loading.emit(False)
        
        threading.Thread(target=fetch_token_thread, daemon=True).start()

    def fetch_game_mask_id(self, game_name):
        if self.stream:
            try:
                categories = self.stream.search(game_name)
                for category in categories:
                    if category['full_name'] == game_name:
                        self.game_mask_id = category['game_mask_id']
                        return
                self.game_mask_id = ""
            except Exception as e:
                QMessageBox.warning(self, "Search Error", f"Failed to search games: {str(e)}")

    def handle_game_search(self, text):
        if text and self.stream:
            threading.Thread(target=self.search_games, args=(text,)).start()
        else:
            self.suggestions_list.hide()

    def search_games(self, text):
        try:
            categories = self.stream.search(text)
            self.update_suggestions.emit(categories)
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Game search failed: {str(e)}")

    def update_suggestions_list(self, categories):
        self.suggestions_list.clear()
        for category in categories:
            self.suggestions_list.addItem(QListWidgetItem(category['full_name']))
        self.suggestions_list.setVisible(bool(categories))

    def handle_suggestion_selected(self, item):
        self.game_category.setText(item.text())
        self.fetch_game_mask_id(item.text())
        self.suggestions_list.hide()

    def start_stream(self):
        if not self.stream_title.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a stream title before going live.")
            return
        
        self.enable_button.emit("go_live", False)
        self.set_button_text.emit("go_live", "⏳ Starting...")
        self.update_loading.emit(True)
        
        def start_stream_thread():
            try:
                audience_type = "1" if self.mature_checkbox.isChecked() else "0"
                stream_url, stream_key = self.stream.start(
                    self.stream_title.text(),
                    self.game_mask_id,
                    audience_type
                )
                
                if stream_url and stream_key:
                    self.set_stream_info.emit(stream_url, stream_key)
                    self.enable_button.emit("end_live", True)
                    self.enable_button.emit("go_live", False)
                    self.set_button_text.emit("go_live", "▶️ Go Live")
                    self.show_message.emit("✅ Live Started", "Stream started successfully!\n\nYour stream URL and key are ready to use in OBS Studio.", "success")
                else:
                    self.enable_button.emit("go_live", True)
                    self.set_button_text.emit("go_live", "▶️ Go Live")
                    self.show_message.emit("❌ Error", "Failed to start stream! Please check your connection and try again.", "error")
            except Exception as e:
                self.enable_button.emit("go_live", True)
                self.set_button_text.emit("go_live", "▶️ Go Live")
                self.show_message.emit("❌ Error", f"Failed to start stream: {str(e)}", "error")
            finally:
                self.update_loading.emit(False)
        
        threading.Thread(target=start_stream_thread, daemon=True).start()

    def end_stream(self):
        reply = QMessageBox.question(
            self,
            "End Stream",
            "Are you sure you want to end the live stream?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.enable_button.emit("end_live", False)
        self.set_button_text.emit("end_live", "⏳ Ending...")
        self.update_loading.emit(True)
        
        def end_stream_thread():
            try:
                if self.stream.end():
                    self.clear_stream_info.emit()
                    self.enable_button.emit("end_live", False)
                    self.set_button_text.emit("end_live", "⏹️ End Live")
                    self.enable_button.emit("go_live", True)
                    self.show_message.emit("✅ Live Ended", "Stream ended successfully!", "success")
                else:
                    self.enable_button.emit("end_live", True)
                    self.set_button_text.emit("end_live", "⏹️ End Live")
                    self.show_message.emit("❌ Error", "Failed to end stream! Please try again.", "error")
            except Exception as e:
                self.enable_button.emit("end_live", True)
                self.set_button_text.emit("end_live", "⏹️ End Live")
                self.show_message.emit("❌ Error", f"Failed to end stream: {str(e)}", "error")
            finally:
                self.update_loading.emit(False)
        
        threading.Thread(target=end_stream_thread, daemon=True).start()

    def copy_to_clipboard(self, widget):
        text = widget.text()
        if not text:
            QMessageBox.warning(self, "Warning", "Nothing to copy!")
            return
        QApplication.clipboard().setText(text)
        # Show a brief notification instead of blocking message box
        widget.setStyleSheet("border: 2px solid #00d4aa;")
        QTimer.singleShot(1000, lambda: widget.setStyleSheet(""))

    def show_help(self):
        help_text = """1. Apply for LIVE access on Streamlabs
2. Install Streamlabs and login to TikTok
3. Use this app to get Streamlabs token
4. Go live!"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setText(help_text)
        msg.addButton(QMessageBox.Ok)
        msg.exec()


    def check_updates_on_startup(self):
        """Non-blocking update check with GUI notification"""
        # Lazy import heavy modules - only load when checking for updates
        from version_checker import VersionChecker
        from packaging import version
        
        update_info = VersionChecker.check_update()

        if update_info and version.parse(update_info["latest"]) > version.parse(update_info["current"]):
            msg = QMessageBox(self)
            msg.setWindowTitle("Update Available")
            msg.setText(
                f"Version {update_info['latest']} is available!\n\n"
                f"Current version: {update_info['current']}\n\n"
                "Would you like to download it now?"
            )
            
            # Use standard buttons for better compatibility
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            if msg.exec() == QMessageBox.Yes:
                QDesktopServices.openUrl(update_info["url"])

    def show_donation_reminder(self):
        
        if self.suppress_donation_reminder:
            return
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Support Development")
        msg.setText("Enjoying this app? Consider supporting its development!")
        
        dont_show_again = QCheckBox("Never show this message again")
        msg.setCheckBox(dont_show_again)
        
        # Add buttons
        donate_btn = msg.addButton("Donate Now", QMessageBox.AcceptRole)
        msg.addButton(QMessageBox.Ok)
        
        # Make the "Donate Now" button more prominent
        donate_btn.setStyleSheet("font-weight: bold;")
        
        # Execute the message box
        msg.exec()
        
        if dont_show_again.isChecked():
            self.suppress_donation_reminder = True
            self.save_config(False)
        # Handle button clicks
        if msg.clickedButton() == donate_btn:
            QDesktopServices.openUrl("https://buymeacoffee.com/suntury")

    def open_live_monitor(self):
        QDesktopServices.openUrl("https://livecenter.tiktok.com/live_monitor?lang=en-US")

    def handle_ui_update(self):
        self.load_account_info()
    
    def handle_token_loaded(self, token):
        """Thread-safe handler for token loading"""
        self.token_entry.setText(token)
        # Create Stream object only once
        if self.stream is None or not hasattr(self.stream, 's') or \
           self.stream.s.headers.get('authorization') != f"Bearer {token}":
            self.stream = Stream(token)
        self.load_account_info()
        self.fetch_game_mask_id(self.game_category.text())
    
    def handle_show_message(self, title, message, msg_type):
        """Thread-safe handler for showing messages"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "success":
            QMessageBox.information(self, title, message)
    
    def handle_update_loading(self, show):
        """Thread-safe handler for loading indicator"""
        if show:
            self.loading_progress.show()
        else:
            self.loading_progress.hide()
    
    def handle_enable_button(self, button_name, enabled):
        """Thread-safe handler for enabling/disabling buttons"""
        if button_name == "load_local":
            self.load_local_btn.setEnabled(enabled)
        elif button_name == "load_online":
            self.load_online_btn.setEnabled(enabled)
        elif button_name == "go_live":
            self.go_live_btn.setEnabled(enabled)
        elif button_name == "end_live":
            self.end_live_btn.setEnabled(enabled)
    
    def handle_set_button_text(self, button_name, text):
        """Thread-safe handler for setting button text"""
        if button_name == "go_live":
            self.go_live_btn.setText(text)
        elif button_name == "end_live":
            self.end_live_btn.setText(text)
    
    def handle_set_stream_info(self, url, key):
        """Thread-safe handler for setting stream URL and key"""
        self.stream_url.setText(url)
        self.stream_key.setText(key)
        self.stream_key.setEchoMode(QLineEdit.Password)  # Keep key hidden
    
    def handle_clear_stream_info(self):
        """Thread-safe handler for clearing stream URL and key"""
        self.stream_url.clear()
        self.stream_key.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application icon BEFORE creating the window (important for Windows taskbar)
    app_icon = StreamApp.get_app_icon()
    app.setWindowIcon(app_icon)
    
    window = StreamApp()
    window.show()
    sys.exit(app.exec())