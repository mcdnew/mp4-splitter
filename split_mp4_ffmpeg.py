#!/usr/bin/env python3
"""
Split an MP4 into N chunks using FFmpeg stream copy (no re-encoding).
Compatible with Python 3.8+.

Now also accepts a DIRECTORY path:
- If you pass a folder, it will list .mp4 files inside and let you pick one.
"""

import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

USAGE_TEXT = r"""
==============================================================
MP4 SPLITTER (FFmpeg - No Re-encoding, Lossless & Fast)
==============================================================

This script splits an .mp4 video into a number of equal chunks
using FFmpeg's stream copy mode (-c copy). This ensures:
  - No quality loss (original data preserved)
  - Much faster than re-encoding
  - Slightly approximate cut points (aligned to keyframes)

--------------------------------------------------------------
REQUIREMENTS:
--------------------------------------------------------------
1. FFmpeg & FFprobe must be installed and in your PATH.
   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/
     Extract, add the 'bin' folder to PATH.
   - macOS: brew install ffmpeg
   - Linux (Debian/Ubuntu): sudo apt install ffmpeg
2. The input can be:
   - A path to an .mp4 file, OR
   - A directory containing one or more .mp4 files (you'll pick one)
3. Python 3.8+ recommended.

--------------------------------------------------------------
USAGE EXAMPLES:
--------------------------------------------------------------
Interactive mode (will ask for path and chunk count):
    python split_mp4_ffmpeg.py

Direct mode (no prompts):
    python split_mp4_ffmpeg.py "/path/video.mp4" 4

Specify output directory:
    python split_mp4_ffmpeg.py "/path/video.mp4" 4 "/path/output"

Pass a directory and choose a file interactively:
    python split_mp4_ffmpeg.py "/path/to/folder" 3

--------------------------------------------------------------
OUTPUT:
--------------------------------------------------------------
Creates:
    video_part01.mp4, video_part02.mp4, ...
in the same folder as the original (or in the chosen output dir).

--------------------------------------------------------------
NOTE:
--------------------------------------------------------------
Because we're not re-encoding, cut points will be at keyframes.
This means chunk durations may vary slightly.
==============================================================
"""

def check_deps():
    """Ensure ffmpeg and ffprobe are available."""
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("ERROR: FFmpeg and FFprobe must be installed and on your PATH.")
        sys.exit(1)

def ffprobe_duration(path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
    return float(out)

def pick_mp4_from_dir(folder: Path) -> Path:
    """List .mp4 files in folder and let the user pick one; raise if none."""
    mp4s: List[Path] = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"])
    if not mp4s:
        raise FileNotFoundError(f"No .mp4 files found in directory: {folder}")
    if len(mp4s) == 1:
        print(f"Found one MP4: {mp4s[0].name}")
        return mp4s[0]
    print("\nMultiple .mp4 files found. Choose one:")
    for i, p in enumerate(mp4s, start=1):
        print(f"[{i}] {p.name}")
    while True:
        choice = input(f"Enter a number (1-{len(mp4s)}): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(mp4s):
                return mp4s[idx - 1]
        print("Invalid selection. Try again.")

def resolve_input_path(path_str: str) -> Path:
    """Expand ~ and resolve path without requiring existence."""
    return Path(path_str).expanduser()

def ensure_video_path(path: Path) -> Path:
    """Accept a file or a directory. If directory, prompt user to pick an .mp4."""
    if path.is_dir():
        return pick_mp4_from_dir(path)
    # If not dir, it should be an existing file
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    if path.suffix.lower() != ".mp4":
        raise ValueError(f"Input file must be an .mp4: {path}")
    return path

def split_video_stream_copy(file_path: Path, num_chunks: int, out_dir: Optional[Path] = None):
    """Split MP4 into num_chunks using FFmpeg without re-encoding."""
    if num_chunks <= 0:
        raise ValueError("Number of chunks must be greater than zero.")
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    duration = ffprobe_duration(file_path)
    sec_per_chunk = duration / num_chunks

    base = file_path.stem
    out_dir = out_dir or file_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    digits = max(2, int(math.ceil(math.log10(num_chunks + 1))))
    template = f"{base}_part%0{digits}d.mp4"
    output_template = str(out_dir / template)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i", str(file_path),
        "-map", "0",
        "-c", "copy",
        "-f", "segment",
        "-segment_time", f"{sec_per_chunk:.6f}",
        "-reset_timestamps", "1",
        "-avoid_negative_ts", "make_zero",
        output_template,
    ]

    print(f"\nInput: {file_path}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Target chunks: {num_chunks}")
    print(f"Approx seconds per chunk: {sec_per_chunk:.2f}")
    print(f"Output pattern: {output_template}")
    print("\nRunning FFmpeg...\n")

    proc = subprocess.Popen(cmd)
    proc.wait()

    if proc.returncode == 0:
        print("\n✅ Done! Files saved in:", out_dir)
    else:
        print("\n❌ FFmpeg encountered an error.")

def read_args() -> tuple:
    """Parse simplistic argv: [path] [chunks] [outdir] (all optional)."""
    args = sys.argv[1:]
    if len(args) >= 2:
        in_path = resolve_input_path(args[0])
        chunks = int(args[1])
        outdir = resolve_input_path(args[2]) if len(args) >= 3 else None
        return in_path, chunks, outdir
    # Interactive fallback
    in_path = resolve_input_path(input("Enter path to your .mp4 file OR a directory containing .mp4s: ").strip())
    chunks = int(input("Enter number of chunks: ").strip())
    outdir_in = input("Output directory (leave blank for same folder): ").strip()
    outdir = resolve_input_path(outdir_in) if outdir_in else None
    return in_path, chunks, outdir

if __name__ == "__main__":
    print(USAGE_TEXT)
    check_deps()

    try:
        in_path, num_chunks, out_dir = read_args()
        video_path = ensure_video_path(in_path)
        split_video_stream_copy(video_path, num_chunks, out_dir)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(2)

