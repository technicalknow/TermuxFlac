#!/usr/bin/env python3
import os, sqlite3, mimetypes, threading, time
from pathlib import Path
from flask import Flask, jsonify, request, send_file, abort, send_from_directory, Response
from mutagen.flac import FLAC

BASE = Path(__file__).resolve().parent
MUSIC_DIR = Path(os.environ.get("MUSIC_DIR", str(BASE / "music"))).expanduser().resolve()
DB_PATH = BASE / "library.db"
WEB_DIR = BASE / "web"

app = Flask(__name__, static_folder=None)
scan_lock = threading.Lock()

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        artist TEXT,
        album_artist TEXT,
        album TEXT,
        genre TEXT,
        year TEXT,
        track_no INTEGER,
        disc_no INTEGER,
        duration REAL DEFAULT 0,
        size INTEGER DEFAULT 0,
        mtime REAL DEFAULT 0,
        has_art INTEGER DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title);
    CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist);
    CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album);
    """)
    conn.commit()
    conn.close()

def first(tags, key, default=""):
    v = tags.get(key)
    return str(v[0]) if v else default

def int_tag(tags, key):
    try:
        return int(first(tags, key, "0").split("/")[0])
    except Exception:
        return 0

def scan_library():
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    with scan_lock:
        conn = db()
        seen=set()
        for p in MUSIC_DIR.rglob("*.flac"):
            if not p.is_file():
                continue
            seen.add(str(p))
            try:
                st=p.stat()
                audio=FLAC(str(p))
                tags=audio
                title=first(tags,"title",p.stem)
                artist=first(tags,"artist","Unknown Artist")
                album_artist=first(tags,"albumartist",artist)
                album=first(tags,"album","Unknown Album")
                genre=first(tags,"genre","")
                year=first(tags,"date","")
                track_no=int_tag(tags,"tracknumber")
                disc_no=int_tag(tags,"discnumber") or 1
                duration=float(getattr(audio.info,"length",0) or 0)
                has_art=1 if audio.pictures else 0
                conn.execute("""
                INSERT INTO tracks(path,title,artist,album_artist,album,genre,year,track_no,disc_no,duration,size,mtime,has_art)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(path) DO UPDATE SET
                  title=excluded.title, artist=excluded.artist,
                  album_artist=excluded.album_artist, album=excluded.album,
                  genre=excluded.genre, year=excluded.year,
                  track_no=excluded.track_no, disc_no=excluded.disc_no,
                  duration=excluded.duration, size=excluded.size,
                  mtime=excluded.mtime, has_art=excluded.has_art
                """,(str(p),title,artist,album_artist,album,genre,year,
                     track_no,disc_no,duration,st.st_size,st.st_mtime,has_art))
            except Exception as e:
                print("Skipping:", p, e)
        if seen:
            qmarks=",".join("?"*len(seen))
            conn.execute(f"DELETE FROM tracks WHERE path NOT IN ({qmarks})", tuple(seen))
        else:
            conn.execute("DELETE FROM tracks")
        conn.commit()
        conn.close()

def track_json(r):
    d=dict(r)
    d["stream"]=f"/api/stream/{d['id']}"
    d["art"]=f"/api/art/{d['id']}" if d["has_art"] else "/api/art/default"
    d.pop("path",None)
    return d

@app.route("/")
def index():
    return send_from_directory(WEB_DIR,"index.html")

@app.route("/<path:name>")
def web_asset(name):
    p=WEB_DIR/name
    if p.exists() and p.is_file():
        return send_from_directory(WEB_DIR,name)
    abort(404)

@app.get("/api/library")
def library():
    q=request.args.get("q","").strip()
    conn=db()
    if q:
        like=f"%{q}%"
        rows=conn.execute("""
        SELECT * FROM tracks
        WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR album_artist LIKE ?
        ORDER BY album_artist, album, disc_no, track_no, title
        """,(like,like,like,like)).fetchall()
    else:
        rows=conn.execute("""
        SELECT * FROM tracks
        ORDER BY album_artist, album, disc_no, track_no, title
        """).fetchall()
    conn.close()
    return jsonify([track_json(r) for r in rows])

@app.get("/api/albums")
def albums():
    conn=db()
    rows=conn.execute("""
    SELECT album_artist, album, MIN(id) AS cover_id, COUNT(*) AS track_count
    FROM tracks GROUP BY album_artist, album
    ORDER BY album_artist, album
    """).fetchall()
    conn.close()
    return jsonify([{
        "artist":r["album_artist"], "album":r["album"],
        "cover":f"/api/art/{r['cover_id']}", "track_count":r["track_count"]
    } for r in rows])

@app.post("/api/scan")
def scan():
    scan_library()
    return jsonify({"ok":True})

@app.get("/api/art/<id>")
def art(id):
    if id == "default":
        return send_from_directory(WEB_DIR,"default-art.svg", mimetype="image/svg+xml")
    conn=db()
    r=conn.execute("SELECT path FROM tracks WHERE id=?",(id,)).fetchone()
    conn.close()
    if not r: abort(404)
    try:
        audio=FLAC(r["path"])
        if not audio.pictures: abort(404)
        pic=audio.pictures[0]
        return Response(pic.data, mimetype=pic.mime or "image/jpeg",
                        headers={"Cache-Control":"public, max-age=86400"})
    except Exception:
        abort(404)

@app.get("/api/stream/<id>")
def stream(id):
    conn=db()
    r=conn.execute("SELECT path FROM tracks WHERE id=?",(id,)).fetchone()
    conn.close()
    if not r or not Path(r["path"]).is_file(): abort(404)
    path=Path(r["path"])
    size=path.stat().st_size
    range_header=request.headers.get("Range")
    if not range_header:
        return send_file(path, mimetype="audio/flac", conditional=True)
    try:
        ranges=range_header.replace("bytes=","").split("-")
        start=int(ranges[0]) if ranges[0] else 0
        end=int(ranges[1]) if len(ranges)>1 and ranges[1] else size-1
        start=max(0,start); end=min(end,size-1)
        if start>end: raise ValueError
    except Exception:
        return Response(status=416, headers={"Content-Range":f"bytes */{size}"})
    length=end-start+1
    def generate():
        with open(path,"rb") as f:
            f.seek(start)
            remaining=length
            while remaining:
                chunk=f.read(min(1024*1024,remaining))
                if not chunk: break
                remaining-=len(chunk)
                yield chunk
    return Response(generate(),206,mimetype="audio/flac",
                    headers={
                        "Content-Range":f"bytes {start}-{end}/{size}",
                        "Accept-Ranges":"bytes",
                        "Content-Length":str(length),
                        "Cache-Control":"no-cache"
                    })

if __name__=="__main__":
    init_db()
    if not any((BASE/"music").iterdir()) if (BASE/"music").exists() else True:
        (BASE/"music").mkdir(exist_ok=True)
    print(f"Music directory: {MUSIC_DIR}")
    print("Scanning library...")
    scan_library()
    print("Open http://TABLET_IP:8000 on your phone")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8000")), threaded=True)
