# TermuxFLAC

A lightweight LAN FLAC music server + mobile web player for Android/Termux.

## Features

- Streams original FLAC files; no transcoding
- HTTP Range requests for efficient seeking
- Reads FLAC metadata with Mutagen
- Extracts embedded album artwork
- SQLite library index
- Search by title/artist/album
- Queue with persistent localStorage
- Play/pause/next/previous
- Shuffle and repeat
- Android lock-screen/media controls via Media Session API
- Installable as a PWA
- Mobile-first UI

## Install on the tablet

```bash
pkg update
pkg install python
termux-setup-storage
cd ~/storage/shared
# Put this project somewhere accessible, e.g. ~/termuxflac
cd ~/termuxflac
python -m pip install -r requirements.txt
```

If your music is in `~/storage/music`, start with:

```bash
MUSIC_DIR=~/storage/music python server.py
```

Or edit the path/environment to wherever your FLAC collection lives.

Find the tablet's Wi-Fi IP:

```bash
ip addr show wlan0
```

Then on the phone open:

```text
http://TABLET_IP:8000
```

Example:

```text
http://192.168.1.25:8000
```

## Notes

- Keep the tablet and phone on the same Wi-Fi network.
- The first startup scans all FLAC files and builds `library.db`.
- After adding/removing music, press the ↻ scan button.
- The server does not transcode FLAC, so the phone receives the original lossless stream.
- For remote/off-Wi-Fi access, use a VPN such as Tailscale rather than exposing port 8000 directly to the internet.
- For battery life, Android may suspend Termux in the background. Termux:WakeLock can help during listening sessions.

## Optional: launch script

```bash
#!/data/data/com.termux/files/usr/bin/bash
export MUSIC_DIR="$HOME/storage/music"
cd "$HOME/termuxflac"
python server.py
```

Save as `start.sh`, then:

```bash
chmod +x start.sh
./start.sh
```
