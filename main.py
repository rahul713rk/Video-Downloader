# main.py
import os
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow

from core.downloader import DownloadManager
from ui.main_window import MainWindowUI


class YTDLPGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._init_download_manager()
        self._connect_signals()
        self._setup_window()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.ui = MainWindowUI()
        self.setCentralWidget(self.ui)

    def _init_download_manager(self) -> None:
        """Initialize the download manager."""
        self.download_manager = DownloadManager()

    def _connect_signals(self) -> None:
        """Connect all UI signals to their handlers."""
        # Download manager signals
        self.download_manager.progress_updated.connect(self.ui.update_progress)
        self.download_manager.status_updated.connect(self.ui.status_label.setText)
        self.download_manager.speed_updated.connect(self.ui.speed_label.setText)
        self.download_manager.eta_updated.connect(self.ui.eta_label.setText)
        self.download_manager.download_complete.connect(self._on_download_complete)
        self.download_manager.download_stopped.connect(self._on_download_stopped)

        # UI buttons
        self.ui.download_button.clicked.connect(self.start_download)
        self.ui.stop_button.clicked.connect(self.download_manager.stop_download)
        self.ui.browse_button.clicked.connect(self.ui.browse_output_directory)

    def _setup_window(self) -> None:
        """Configure main window settings."""
        self.setWindowTitle("Video Downloader")
        self.setMinimumSize(800, 600)  

    def start_download(self) -> None:
        """Start download with current settings."""
        url = self.ui.url_input.text().strip()
        if not url:
            self.ui.status_label.setText("Please enter a URL")
            return

        format_ = self.ui.format_combo.currentText()
        output_path = self.ui.output_path.text() or os.path.expanduser("~/Downloads")

        # Get all options
        options = {
            'custom_format': self.ui.custom_format_input.text() if format_ == "Custom format code..." else None,
            'audio_format': self.ui.audio_format_combo.currentText(),
            'audio_quality': self.ui.audio_quality_slider.value(),
            'remux_format': self.ui.remux_combo.currentText(),
            'subtitles': self.ui.subtitles_check.isChecked(),
            'thumbnail': self.ui.thumbnail_check.isChecked(),
            'metadata': self.ui.metadata_check.isChecked(),
            'chapters': self.ui.chapters_check.isChecked(),
            'split_chapters': self.ui.split_chapters_check.isChecked(),
            'playlist': self.ui.playlist_check.isChecked(),
            'sponsorblock': self.ui.sponsorblock_check.isChecked(),
            'sponsorblock_categories': self.ui.sponsorblock_categories.text().strip() or 'all'
        }

        # Update UI state
        self.ui.set_download_state(False)
        self.ui.reset_progress()

        # Start download
        self.download_manager.start_download(url, format_, output_path, options)

    def _on_download_complete(self, success: bool, message: str) -> None:
        """Handle download completion."""
        self.ui.set_download_state(True)
        if not success:
            self.ui.status_label.setText(f"Error: {message}")

    def _on_download_stopped(self) -> None:
        """Handle download stopped by user."""
        self.ui.set_download_state(True)
        self.ui.status_label.setText("Download stopped")

    def closeEvent(self, event) -> None:
        """Clean up resources when window closes."""
        self.download_manager.cleanup()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set application style
    
    # Set application metadata
    app.setApplicationName("yt-dlp GUI")
    app.setApplicationVersion("1.0")
    
    window = YTDLPGUI()
    window.show()
    sys.exit(app.exec())