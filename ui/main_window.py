# ui/main_window.py
import os
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QFileDialog, QFormLayout, QCheckBox, QGroupBox,
    QSlider, QTabWidget
)


class MainWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize all UI components."""
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create basic and advanced tabs
        self.basic_tab = QWidget()
        self.advanced_tab = QWidget()
        
        self.tabs.addTab(self.basic_tab, "Basic")
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        # Setup basic tab
        self._setup_basic_tab()
        
        # Setup advanced tab
        self._setup_advanced_tab()
        
        # Add progress and action buttons to main layout (below tabs)
        self._setup_progress_section()
        self._setup_action_buttons()

    def _setup_basic_tab(self) -> None:
        """Setup the basic options tab."""
        basic_layout = QVBoxLayout()
        self.basic_tab.setLayout(basic_layout)
        
        self._setup_url_section()
        self._setup_format_section()
        self._setup_output_section()
        
        basic_layout.addWidget(self.url_group)
        basic_layout.addWidget(self.format_group)
        basic_layout.addWidget(self.output_group)
        basic_layout.addStretch()  # Push content to top

    def _setup_advanced_tab(self) -> None:
        """Setup the advanced options tab."""
        advanced_layout = QVBoxLayout()
        self.advanced_tab.setLayout(advanced_layout)
        
        self._setup_additional_options()
        advanced_layout.addWidget(self.advance_group)
        advanced_layout.addStretch()  # Push content to top

    def _setup_url_section(self) -> None:
        """URL input section."""
        self.url_group = QGroupBox("Video URL")
        url_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.url_input)
        
        self.url_group.setLayout(url_layout)

    def _setup_format_section(self) -> None:
        """Format selection section with expanded options."""
        self.format_group = QGroupBox("Download Options")
        form_layout = QFormLayout()
        
        # Main format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Best (video+audio)",
            "Best video only",
            "Best audio only",
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p",
            "Worst (video+audio)",
            "Custom format code..."
        ])
        form_layout.addRow("Format:", self.format_combo)
        
        # Custom format code input
        self.custom_format_layout = QHBoxLayout()
        self.custom_format_label = QLabel("Custom format : ")
        self.custom_format_input = QLineEdit()
        self.custom_format_input.setPlaceholderText("e.g. bestvideo[height<=1080]+bestaudio/best")
        self.custom_format_input.setVisible(False)
        self.custom_format_label.setVisible(False)
        self.custom_format_layout.addWidget(self.custom_format_label)
        self.custom_format_layout.addWidget(self.custom_format_input)
        form_layout.addRow(self.custom_format_layout)
        
        # Connect format combo change
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        
        # Audio format selection
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems([
            "best", "aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"
        ])
        form_layout.addRow("Audio format:", self.audio_format_combo)
        
        # Audio quality
        self.audio_quality_slider = QSlider(Qt.Horizontal)
        self.audio_quality_slider.setRange(0, 10)
        self.audio_quality_slider.setValue(5)
        self.audio_quality_label = QLabel("VBR 5 (default)")
        form_layout.addRow("Audio quality:", self.audio_quality_slider)
        form_layout.addRow("", self.audio_quality_label)
        self.audio_quality_slider.valueChanged.connect(
            lambda v: self.audio_quality_label.setText(f"VBR {v}" if v < 10 else "Lossless")
        )
        
        # Remux options
        self.remux_combo = QComboBox()
        self.remux_combo.addItems([
            "Default", "mp4", "mkv", "webm", "mov", "flv", "avi"
        ])
        form_layout.addRow("Video Format:", self.remux_combo)
        
        # Playlist options
        self.playlist_check = QCheckBox("Download entire playlist")
        self.playlist_check.setChecked(True)
        form_layout.addRow(self.playlist_check)
        
        self.format_group.setLayout(form_layout)

    def _on_format_changed(self, text: str) -> None:
        """Show/hide custom format input based on selection."""
        self.custom_format_input.setVisible(text == "Custom format code...")
        self.custom_format_label.setVisible(text == "Custom format code...")

    def _setup_additional_options(self) -> None:
        """Additional download options with more features."""
        self.advance_group = QGroupBox("Post-Processing Options")
        options_layout = QVBoxLayout()
        
        # Container for checkboxes
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        
        # Subtitles
        self.subtitles_check = QCheckBox("Download subtitles")
        checkbox_layout.addWidget(self.subtitles_check)
        
        # Thumbnail
        self.thumbnail_check = QCheckBox("Download thumbnail")
        checkbox_layout.addWidget(self.thumbnail_check)
        
        # Metadata
        self.metadata_check = QCheckBox("Embed metadata")
        checkbox_layout.addWidget(self.metadata_check)
        
        # Chapters
        self.chapters_check = QCheckBox("Embed chapters")
        checkbox_layout.addWidget(self.chapters_check)
        
        # Split chapters
        self.split_chapters_check = QCheckBox("Split by chapters")
        checkbox_layout.addWidget(self.split_chapters_check)
        
        # SponsorBlock
        self.sponsorblock_check = QCheckBox("Remove sponsored segments")
        checkbox_layout.addWidget(self.sponsorblock_check)
        
        options_layout.addWidget(checkbox_container)
        
        # SponsorBlock categories
        self.sponsorblock_categories = QLineEdit()
        self.sponsorblock_categories.setPlaceholderText("sponsor,intro,outro (leave blank for all)")
        options_layout.addWidget(QLabel("SponsorBlock categories:"))
        options_layout.addWidget(self.sponsorblock_categories)
        
        self.advance_group.setLayout(options_layout)

    def _setup_output_section(self) -> None:
        """Output location section."""
        self.output_group = QGroupBox("Output Options")
        output_layout = QVBoxLayout()
        
        # Output path
        path_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output folder...")
        self.browse_button = QPushButton("Browse...")
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(self.browse_button)
        output_layout.addLayout(path_layout)
        
        self.output_group.setLayout(output_layout)

    def _setup_progress_section(self) -> None:
        """Progress display section."""
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        
        # Status labels
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.speed_label = QLabel("Speed: -")
        self.eta_label = QLabel("ETA: -")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.speed_label)
        status_layout.addWidget(self.eta_label)
        
        progress_layout.addLayout(status_layout)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)

    def _setup_action_buttons(self) -> None:
        """Action buttons section."""
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Start Download")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.stop_button)
        self.main_layout.addLayout(button_layout)

    def browse_output_directory(self) -> None:
        """Open directory dialog for output path."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_path.text() or os.path.expanduser("~")
        )
        if directory:
            self.output_path.setText(directory)

    def set_download_state(self, enabled: bool) -> None:
        """Enable/disable download controls."""
        self.download_button.setEnabled(enabled)
        self.stop_button.setEnabled(not enabled)
        self.url_input.setEnabled(enabled)
        self.format_combo.setEnabled(enabled)

    def reset_progress(self) -> None:
        """Reset progress indicators."""
        self.progress_bar.setValue(0)
        self.speed_label.setText("Speed: -")
        self.eta_label.setText("ETA: -")

    def update_progress(self, value: int) -> None:
        """Update progress bar value."""
        self.progress_bar.setValue(value)