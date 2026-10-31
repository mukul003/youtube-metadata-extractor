# YouTube Metadata & HD Thumbnail Studio

A fast, modern web and command-line application to inspect, copy, and download comprehensive metadata and high-definition thumbnails from any YouTube video.

---

## 🌟 Key Features

- **Metadata Inspection**:
  - **Title**: Clean display with character count and 1-click copy.
  - **Category**: Primary category with direct copy.
  - **Date Published**: Human-readable date (`October 25, 2009`) & ISO format (`2009-10-25`) with direct copy.
  - **Description**: Full formatted text with word/char counters, preserved formatting, and direct copy.
  - **Tags & Keywords**: Interactive tag cloud — **click any tag chip to copy it individually**, or copy all tags as comma-separated or `#hashtags`.
  - **Statistics**: Duration, view count, like count, channel info.
- **HD Thumbnail Downloader**:
  - Live preview of Maximum Resolution (`1080p Full HD`, `720p HD`, `480p SD`, `360p`).
  - **1-Click Direct Download**: Saves high-resolution `.jpg` directly to your downloads.
  - Copy Thumbnail direct image URL.
- **Individual Copy Functionality**:
  - Every card features an individual copy button with instant checkmark visual feedback and toast notification.
- **Export & Download**:
  - Download HD Thumbnail (`.jpg`).
  - Download all metadata as JSON (`.json`).
  - Download summary as plain text (`.txt`).
  - Download summary as formatted Markdown (`.md`).
  - Download tags list (`.txt`).
  - Download description (`.txt`).
- **No API Key Required**: Powered by `yt-dlp` with multi-client mobile fallback for speed, accuracy, and reliability.
- **Dark & Light Mode**: Sleek glassmorphic user interface.

---

## 🚀 Quick Start (Stop & Start with run.bat)

### Double-click Launcher (Windows)
Double-click **`run.bat`** (or right-click **`run.ps1`** -> "Run with PowerShell").

> [!NOTE]
> **Automatic Stop & Start**: `run.bat` automatically detects and terminates any previously running instance on port 5000 before launching fresh, preventing port conflicts (`Address already in use`) and ensuring updated code is loaded every time.

---

## 💻 CLI Mode (Terminal Usage)

You can also use this tool directly from your command terminal without opening the web interface:

```powershell
# Inspect video metadata
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download the HD thumbnail directly
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --download-thumb

# Output raw JSON
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --json

# Save metadata JSON, text summary, and HD thumbnail together
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --save-all
```

---

## 📁 Project Structure

```
youtube-metadata-extractor/
├── .venv/                      # Isolated Python Virtual Environment
├── app.py                      # Flask Application Server & API
├── extractor.py                # YouTube metadata & HD thumbnail engine (yt-dlp + fallbacks)
├── cli.py                      # Command-line interface
├── run.bat                     # Windows stop & start launcher
├── run.ps1                     # Windows PowerShell stop & start launcher
├── requirements.txt            # Python dependencies (yt-dlp, Flask, requests)
├── templates/
│   └── index.html              # Responsive Web UI
├── static/
│   ├── css/
│   │   └── style.css           # Styling, themes, and animations
│   └── js/
│       └── app.js              # Copy handlers, download triggers, UI interactions
└── README.md                   # Full documentation
```
