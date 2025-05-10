# core/downloader.py
import os
import threading
from typing import Dict, Any, Optional

from PySide6.QtCore import QObject, Signal
from yt_dlp import YoutubeDL


class DownloadManager(QObject):
    """Handles video downloads using yt-dlp in a separate thread."""
    
    # Signals to update UI
    progress_updated = Signal(int)  # percentage
    status_updated = Signal(str)
    speed_updated = Signal(str)
    eta_updated = Signal(str)
    download_complete = Signal(bool, str)  # success, message
    download_stopped = Signal()

    def __init__(self):
        super().__init__()
        self._stop_flag = False
        self._download_thread: Optional[threading.Thread] = None
        self._ydl_opts: Dict[str, Any] = {}

    def start_download(self, url: str, format_label: str, output_path: str, options: Dict[str, bool]) -> None:
        """Start a download in a separate thread."""
        if self._download_thread and self._download_thread.is_alive():
            self.status_updated.emit("A download is already in progress")
            return

        self._stop_flag = False
        self._ydl_opts = self._build_ydl_options(format_label, output_path, options)
        
        self._download_thread = threading.Thread(
            target=self._download_video,
            args=(url,),
            daemon=True
        )
        self._download_thread.start()

    def stop_download(self) -> None:
        """Stop the current download."""
        self._stop_flag = True
        self.status_updated.emit("Stopping download...")
        self.download_stopped.emit()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self._download_thread and self._download_thread.is_alive():
            self.stop_download()
            self._download_thread.join(timeout=2)

    # core/downloader.py (updated sections)
    def _build_ydl_options(self, format_label: str, output_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build yt-dlp options dictionary with expanded format options."""
        # Determine default formats
        default_video_ext = options['remux_format'].lower() if options.get('remux_format') and options['remux_format'] != "Default" else 'mp4'
        default_audio_ext = options['audio_format'].lower() if options.get('audio_format') else 'm4a'
        
        # Audio-only formats
        audio_only_formats = ["Best audio only"]
        
        format_map = {
            "Best (video+audio)": f"bestvideo[ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[ext={default_video_ext}]/best",
            "Best video only": f"bestvideo[ext={default_video_ext}]",
            "Best audio only": f"bestaudio[ext={default_audio_ext}]",
            "1440p": f"bestvideo[height<=1440][ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[height<=1440][ext={default_video_ext}]",
            "1080p": f"bestvideo[height<=1080][ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[height<=1080][ext={default_video_ext}]",
            "720p": f"bestvideo[height<=720][ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[height<=720][ext={default_video_ext}]",
            "480p": f"bestvideo[height<=480][ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[height<=480][ext={default_video_ext}]",
            "360p": f"bestvideo[height<=360][ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[height<=360][ext={default_video_ext}]",
            "Worst (video+audio)": f"worstvideo[ext={default_video_ext}]+worstaudio[ext={default_audio_ext}]/worst[ext={default_video_ext}]",
            "Custom format code...": options.get('custom_format', 
                f"bestvideo[ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[ext={default_video_ext}]/best")
        }

        ydl_opts = {
            'format': format_map.get(format_label, 
                f"bestvideo[ext={default_video_ext}]+bestaudio[ext={default_audio_ext}]/best[ext={default_video_ext}]/best"),
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'restrictfilenames': True,
            'merge_output_format': default_video_ext,
            'postprocessors': []
        }

        # Audio options
        if options.get('audio_format'):
            ydl_opts['audioformat'] = options['audio_format']
            ydl_opts['audioquality'] = str(options['audio_quality'])

        # For audio-only downloads, ensure we use the selected audio format
        if format_label in audio_only_formats:
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': default_audio_ext,
                'preferredquality': str(options['audio_quality'])
            })
        else:
            # For video downloads, add video conversion postprocessor
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': default_video_ext
            })

        # Remux options (only if explicitly selected and not Default)
        if options.get('remux_format') and options['remux_format'] != "Default":
            ydl_opts['remuxvideo'] = options['remux_format']
            # Don't convert if we're remuxing
            ydl_opts['postprocessors'] = []

        # Post-processing options
        if options.get('subtitles'):
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['all']
            ydl_opts['embedsubtitles'] = True

        if options.get('thumbnail'):
            ydl_opts['writethumbnail'] = True
            ydl_opts['embedthumbnail'] = True

        if options.get('metadata'):
            ydl_opts['addmetadata'] = True

        if options.get('chapters'):
            ydl_opts['embedchapters'] = True

        if options.get('split_chapters'):
            ydl_opts['splitchapters'] = True

        # Playlist options
        if options.get('playlist'):
            ydl_opts['noplaylist'] = False
        else:
            ydl_opts['noplaylist'] = True

        # SponsorBlock options
        if options.get('sponsorblock'):
            ydl_opts['sponsorblock_remove'] = options.get('sponsorblock_categories', 'all')

        return ydl_opts

    def _download_video(self, url: str) -> None:
        """Download video using yt-dlp (runs in separate thread)."""
        try:
            self.status_updated.emit("Preparing download...")

            with YoutubeDL(self._ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Failed to extract video info")

                self.status_updated.emit(f"Downloading: {info.get('title', 'video')}")
                ydl.download([url])

                if self._stop_flag:
                    self.status_updated.emit("Download cancelled")
                    self.download_stopped.emit()
                    return

                output_file = ydl.prepare_filename(info)
                self.status_updated.emit("Download complete")
                self.download_complete.emit(True, output_file)

        except Exception as e:
            self.status_updated.emit(f"Error: {str(e)}")
            self.download_complete.emit(False, str(e))

    def _progress_hook(self, progress: Dict[str, Any]) -> None:
        """Handle progress updates from yt-dlp."""
        if self._stop_flag:
            raise Exception("Download stopped by user")

        if progress['status'] == 'downloading':
            if progress.get('total_bytes'):
                percent = progress['downloaded_bytes'] / progress['total_bytes'] * 100
                self.progress_updated.emit(int(percent))
            
            if progress.get('speed'):
                self.speed_updated.emit(f"Speed: {self._format_speed(progress['speed'])}")
            
            if progress.get('eta'):
                self.eta_updated.emit(f"ETA: {self._format_eta(progress['eta'])}")

    @staticmethod
    def _format_speed(speed: float) -> str:
        """Format download speed in human-readable format."""
        if speed < 1024:
            return f"{speed:.1f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / (1024 * 1024):.1f} MB/s"

    @staticmethod
    def _format_eta(seconds: int) -> str:
        """Format ETA in human-readable format."""
        if seconds < 0:
            return "--:--"
        
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"