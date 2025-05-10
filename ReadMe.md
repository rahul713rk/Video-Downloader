# 🎬 Video Downloader

![Video-Downloader banner](https://img.shields.io/badge/Built%20with-PySide6-blue) ![Packaged with-Nuitka-orange](https://img.shields.io/badge/Packaged%20with-Nuitka-orange) ![License-MIT-green](https://img.shields.io/badge/license-MIT-green)

**yt-dlp GUI** is a user-friendly desktop application that wraps the power of [yt-dlp](https://github.com/yt-dlp/yt-dlp) with a clean, intuitive interface built using **PySide6** (Qt for Python). It lets you download videos and playlists from YouTube and other supported platforms with customizable formats, audio options, subtitle support, and post-processing features.

---

## 🚀 Features

* 🎯 URL input with format selection (video/audio/custom)
* 🎧 Audio-only download with format and VBR quality slider
* 🎞️ Format remuxing (`mp4`, `mkv`, `webm`, etc.)
* 📝 Subtitle, metadata, and thumbnail options
* 🔀 Chapter embedding and splitting
* ⏩ SponsorBlock support with custom categories
* 📂 Output directory selection
* 📶 Live progress updates, speed, and ETA
* ✨ Simple, clean Fusion-themed GUI

---

## 🛠️ Installation

### 📦 From `.deb` Package (Debian/Ubuntu-based systems)

1. Download the `.deb` package:
   
   ```
   wget https://github.com/rahul713rk/Video-Downloader/blob/master/video-downloader.deb
   ```

2. Install it using `dpkg`:
   
   ```bash
   sudo dpkg -i video-downloader.deb
   ```

3. (Optional) Fix missing dependencies:
   
   ```bash
   sudo apt --fix-broken install
   ```

4. Launch from the **Applications menu** or via terminal:
   
   ```bash
   video-downloader
   ```

5. Uninstall using `apt`:
   
   ```bash
   sudo apt-get remove video-downloader
   ```

---

## 🧰 (Optional) Dependencies

The packaged `.deb` file includes all Python dependencies through **Nuitka**, so you don't need to install Python manually. However, make sure `ffmpeg` is installed on your system:

```bash
sudo apt install ffmpeg
```

---

## 📸 Screenshots

![](/assets/ss-01.png)

![](/assets/ss-02.png)

---

## 🤝 Contributing

Pull requests are welcome! If you'd like to contribute, improve UX, fix bugs, or add features, please open an issue or submit a PR.

---
