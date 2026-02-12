import os
import shutil
import tempfile
from typing import List, Callable, Optional

import yt_dlp
from pydub import AudioSegment  # uses ffmpeg from PATH. [web:20]

ProgressCallback = Optional[Callable[[int, str], None]]  # (percent, message)


def _search_and_download_audio(
    singer_name: str,
    n: int,
    download_dir: str,
) -> List[str]:
    """
    Use yt-dlp to search on YouTube and download N audio-only files
    for the given singer into download_dir. Returns list of file paths. [web:24]
    """
    os.makedirs(download_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    search_query = f"ytsearch{n}:{singer_name}"

    audio_files: List[str] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # [web:24][web:22]
        info = ydl.extract_info(search_query, download=True)
        entries = info.get("entries", []) if isinstance(info, dict) else []
        for entry in entries:
            if not entry:
                continue
            title = entry.get("title")
            if not title:
                continue
            file_path = os.path.join(download_dir, f"{title}.mp3")
            if os.path.exists(file_path):
                audio_files.append(file_path)

    if len(audio_files) == 0:
        raise RuntimeError(
            f"No audio files could be downloaded for '{singer_name}'."
        )

    # Use whatever was downloaded, up to n
    audio_files = audio_files[:n]
    return audio_files


def _trim_audios(
    audio_files: List[str],
    seconds: int,
    trimmed_dir: str,
) -> List[str]:
    """
    Load each audio file, trim to first `seconds`, save to trimmed_dir, and
    return list of trimmed file paths. [web:20]
    """
    os.makedirs(trimmed_dir, exist_ok=True)

    trimmed_files: List[str] = []
    max_ms = seconds * 1000

    for idx, path in enumerate(audio_files):
        audio = AudioSegment.from_file(path)  # [web:20]
        trimmed = audio[:max_ms]
        out_path = os.path.join(trimmed_dir, f"trimmed_{idx}.mp3")
        trimmed.export(out_path, format="mp3")  # [web:20]
        trimmed_files.append(out_path)

    return trimmed_files


def _merge_audios(
    trimmed_files: List[str],
    output_file: str,
) -> None:
    """
    Concatenate all trimmed segments and export as output_file. [web:20]
    """
    if not trimmed_files:
        raise ValueError("No trimmed audio files to merge.")

    combined = AudioSegment.empty()  # [web:20]

    for path in trimmed_files:
        segment = AudioSegment.from_file(path)
        combined += segment

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    combined.export(output_file, format="mp3")  # [web:20]


def create_mashup(
    singer_name: str,
    n: int,
    seconds: int,
    output_file: str,
    progress_cb: ProgressCallback = None,
) -> str:
    """
    High-level helper for both CLI and web:
    - create temp dir
    - download N audio files for singer
    - trim to `seconds`
    - merge into `output_file`
    Returns absolute path to final mashup file. [web:24][web:20]
    """

    if n <= 10:
        raise ValueError("NumberOfVideos must be greater than 10.")
    if seconds <= 20:
        raise ValueError("AudioDuration must be greater than 20 seconds.")

    def update(percent: int, msg: str) -> None:
        if progress_cb is not None:
            progress_cb(percent, msg)

    temp_dir = tempfile.mkdtemp(prefix="mashup_")
    download_dir = os.path.join(temp_dir, "downloads")
    trimmed_dir = os.path.join(temp_dir, "trimmed")

    try:
        update(5, "Starting download...")
        audio_files = _search_and_download_audio(singer_name, n, download_dir)
        update(40, f"Downloaded {len(audio_files)} tracks.")

        trimmed_files = _trim_audios(audio_files, seconds, trimmed_dir)
        update(75, "Audio trimmed.")

        output_file_abs = os.path.abspath(output_file)
        _merge_audios(trimmed_files, output_file_abs)
        update(100, "Mashup complete.")

        return output_file_abs
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
