#!/data/data/com.termux/files/usr/bin/bash
export MUSIC_DIR="${MUSIC_DIR:-$HOME/storage/music}"
cd "$(dirname "$0")"
python server.py
