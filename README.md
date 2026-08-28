# TermuxFlac
🎵 Lossless Music Server

A lightweight, self-hosted music server for your personal FLAC music library.

Run it on a computer, server, or even an Android phone using Termux, then access your music library from any device on the same network through a web browser.

The server scans your FLAC files, reads their metadata and embedded album artwork, stores the library in SQLite, and provides direct FLAC streaming through a simple Flask API.

✨ Features

- 🎧 Lossless FLAC streaming
- 📚 Automatic music library scanning
- 🏷️ Reads FLAC metadata including:
  - Title
  - Artist
  - Album artist
  - Album
  - Genre
  - Year
  - Track number
  - Disc number
  - Duration
- 🖼️ Extracts embedded album artwork
- 🔎 Search by title, artist, album, or album artist
- 💿 Album grouping
- ⚡ SQLite-powered music library
- ⏩ HTTP Range support for seeking through tracks
- 📱 Works on Android through Termux
- 🌐 Access your library from other devices on your local network
- 🪶 Lightweight — built with Python, Flask and SQLite

🛠️ Tech Stack

- Python 3
- Flask — web server and API
- Mutagen — FLAC metadata and album-art extraction
- SQLite — music library database
- Termux — optional Android environment

📁 Project Structure

lossless-music-server/
│
├── server.py          # Main Flask server
├── start.sh           # Startup script
├── requirements.txt   # Python dependencies
├── library.db         # Generated music database
│
├── web/               # Web player/interface
│   ├── index.html
│   └── ...
│
└── music/             # Your FLAC music library

«"library.db" and the "music/" directory are generated/used by the server and don't need to contain your music in the GitHub repository.»

---

🚀 Installation

🐧 Linux

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

2. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

The project requires:

Flask
Mutagen

4. Add your music

By default, the server looks for music inside:

./music

Create the directory:

mkdir -p music

Then place your ".flac" files inside it.

For example:

music/
├── Daft Punk/
│   └── Random Access Memories/
│       ├── 01 - Give Life Back to Music.flac
│       ├── 02 - Game of Love.flac
│       └── ...
│
└── Tame Impala/
    └── Currents/
        ├── 01 - Let It Happen.flac
        └── ...

The server recursively searches the music directory, so nested folders are supported.

5. Start the server

python server.py

The server will:

1. Initialize the SQLite database.
2. Scan the music directory.
3. Read the metadata from your FLAC files.
4. Add/update tracks in the library.
5. Start the web server on port "8000".

You should see:

Music directory: ...
Scanning library...
Open http://TABLET_IP:8000 on your phone

---

📱 Android / Termux Installation

This project can also run directly on an Android phone using Termux.

1. Install Termux

Install Termux from a trusted source such as F-Droid or the official Termux project.

2. Give Termux storage permission

termux-setup-storage

Allow the requested permission.

Your Android music directory will then be accessible through:

~/storage/music

3. Clone the repository

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

4. Install Python

pkg update
pkg install python

5. Install the dependencies

pip install -r requirements.txt

6. Start the server

bash start.sh

The included startup script automatically uses:

~/storage/music

as the music directory unless another "MUSIC_DIR" is specified.

---

🎵 Using Your Music Library

Once the server is running, find the IP address of the device running the server.

For example:

192.168.1.25

Then open this from another device connected to the same network:

http://192.168.1.25:8000

You can access the music player from:

- 📱 Android phones
- 💻 Windows PCs
- 🐧 Linux PCs
- 🍎 macOS
- 📟 Tablets
- 🌐 Any device with a modern web browser

---

⚙️ Custom Music Directory

The default music directory depends on how the server is started.

You can override it using the "MUSIC_DIR" environment variable.

Linux

MUSIC_DIR="/path/to/your/music" python server.py

Termux

MUSIC_DIR="$HOME/storage/music" python server.py

For example:

MUSIC_DIR="/mnt/storage/FLAC" python server.py

---

🔄 Rescanning the Library

The server exposes a scan endpoint that rescans the configured music directory.

POST /api/scan

The scanner detects ".flac" files recursively and updates their metadata in the SQLite library.

It also removes database entries for files that are no longer present.

---

🔎 Search

The library API supports searching by:

- Track title
- Artist
- Album
- Album artist

Example:

/api/library?q=Daft

Without a search query, it returns the complete library.

---

🖼️ Album Artwork

If a FLAC file contains embedded artwork, the server extracts and serves the first embedded picture.

Tracks without artwork receive a default artwork image.

---

🎧 Lossless Streaming

The server streams the original ".flac" file directly.

It supports HTTP byte ranges, allowing compatible clients to seek through tracks without requiring the entire file to be downloaded first.

No lossy transcoding is performed by the server.

---

🔒 Network & Privacy

This project is designed primarily for self-hosted/local-network use.

Your music stays on the machine running the server.

By default, the Flask server listens on:

0.0.0.0:8000

This makes it accessible to other devices that can reach the server.

Do not expose the server directly to the public internet without adding appropriate authentication and security measures.

---

🧰 Configuration

The server currently supports these environment variables:

Variable| Default| Description
"MUSIC_DIR"| "./music" / "$HOME/storage/music" via "start.sh"| Location of your FLAC library
"PORT"| "8000"| Port used by the Flask server

Example:

MUSIC_DIR="/media/music" PORT=8080 python server.py

---

📦 Dependencies

The project intentionally keeps its dependency list small:

Flask>=3.0,<4
mutagen>=1.47,<2

---

🤝 Contributing

Contributions, improvements and feature requests are welcome.

Some ideas for future development:

- 🎼 More audio formats
- 🔐 User authentication
- 🌍 Secure remote access
- 📱 Improved mobile UI
- ❤️ Favorites
- 📜 Playlists
- 🔀 Shuffle and queue management
- 📊 Audio quality/codec information
- 🎚️ Equalizer
- 📥 Download support
- 🎵 ReplayGain support

---
