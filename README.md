# MP4 Splitter (FFmpeg, No Re-encode)

Splits an MP4 into **N** chunks using FFmpeg **stream copy** (`-c copy`) for lossless quality and high speed.  
Cut points align to keyframes, so chunk durations are approximate.

---

## Features
- **Lossless**: No quality loss (no re-encoding)
- **Fast**: Only copies streams, doesn’t recompress
- **Cross-platform**: Works on Windows, macOS, Linux
- **Interactive or direct**: Run with prompts or pass arguments
- **Minimal dependencies**: Just Python + FFmpeg

---

## Requirements
- **Python 3.8+**
- **FFmpeg** and **FFprobe** installed and in your PATH
  - **Windows**: [Download from gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, add the `bin` folder to PATH
  - **macOS**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
- An `.mp4` file you want to split

Check installation:
```bash
ffmpeg -version
ffprobe -version
```

---

## Usage

### Interactive mode (prompts for input)
```bash
python split_mp4_ffmpeg.py
```
You will be asked for:
1. Path to the `.mp4` file
2. Number of chunks
3. Optional output directory

### Direct mode (no prompts)
```bash
python split_mp4_ffmpeg.py "/path/video.mp4" 4
```
This splits into **4 chunks** and saves in the same folder.

Specify an output directory:
```bash
python split_mp4_ffmpeg.py "/path/video.mp4" 4 "/path/output"
```

---

## Output
If the input file is `movie.mp4` and you choose 3 chunks, you’ll get:
```
movie_part01.mp4
movie_part02.mp4
movie_part03.mp4
```
Files are numbered with zero padding for correct sorting.

---

## Notes
- No re-encoding means exact split points will be **at keyframes**, not exact seconds.
- For frame-accurate splits, you would need to re-encode (slower, possible quality loss).

---

## License
[MIT License](LICENSE)
