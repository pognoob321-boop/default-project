# ScreenMind — AI Screen Memory

## What It Is
ScreenMind is a free, open-source, always-on screen capture + AI analysis tool. It captures your screen 24/7, analyzes what's on it with Gemma 4 vision, builds searchable memory, and connects to OpenCode via MCP.

## Setup Status: ✅ Running

### Date: 2026-09-04

## What Was Done
- Installed ScreenMind (`pip install screenmind` + AI packages)
- All data lives on `D:\ScreenMind`
- Environment variable: `SCREENMIND_DATA_DIR=D:\ScreenMind`
- llama-server (CPU) installed at `D:\ScreenMind\llama\`
- Auto-start script at `~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/screenmind.bat`
- OpenCode MCP configured in `~/.config/opencode/opencode.jsonc`

## Current State
- ✅ Screen capturing (every ~40s, smart dedup)
- ✅ OCR working (EasyOCR)
- ✅ Embeddings loaded (all-MiniLM-L6-v2, 384 dims)
- ✅ Dashboard: http://127.0.0.1:7777
- ⏳ Gemma 4 E2B model NOT downloaded yet (~3GB)

## How to Use
- Dashboard: http://127.0.0.1:7777
- Hotkeys: `Ctrl+Shift+B` (bookmark), `Ctrl+Shift+P` (pause), `Ctrl+Shift+V` (voice memo)
- After restart, OpenCode can query screen history via MCP

## What Still Needs Doing
Download Gemma 4 model (~3GB):
```powershell
$env:SCREENMIND_DATA_DIR = "D:\ScreenMind"
$env:PYTHONIOENCODING = "utf-8"
& "C:\Users\ZBook\AppData\Local\Programs\Python\Python312\python.exe" -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='ggml-org/gemma-4-E2B-it-GGUF', filename='gemma-4-E2B-it-Q4_0.gguf', local_dir='D:/ScreenMind/models'); hf_hub_download(repo_id='ggml-org/gemma-4-E2B-it-GGUF', filename='mmproj-model-f16.gguf', local_dir='D:/ScreenMind/models')"
```

## Important Notes
- `python` command = Python 3.11 (uv/hermes), NOT 3.12
- Always use: `C:\Users\ZBook\AppData\Local\Programs\Python\Python312\python.exe`
- Set `PYTHONIOENCODING=utf-8` for Windows Unicode issues
- User prefers everything on D: drive

## 2026-10-13 Audit — CPU Spike Fix

**Why CPU was high:** screenmind ran EasyOCR + llama analysis on every ~40s capture, but llama-server was never started and the Gemma model was never downloaded — so the analysis worker burned ~2+ cores per entry on OCR + failed-retry loops (50–75s wasted per entry), permanently. Side effect: Windows `Capability Access Manager Service` (svchost group `-k osprivacy`, shown in Task Manager as the "osprivacy" group) also spiked ~14% from constant capability-access polling.

**Actual live paths (differs from original plan):**
- The HKCU Run key `ScreenMind` (`pythonw.exe -m screenmind`, no `SCREENMIND_DATA_DIR`) is what actually runs at login → live data dir is `~/.screenmind`, NOT `D:\ScreenMind`
- The Startup `screenmind.bat` (sets `SCREENMIND_DATA_DIR=D:\ScreenMind`) loses the port-7777 race and exits
- Duplicate autostart: both Run key and .bat fire; single-instance lock keeps one alive

**Throttling applied (2026-10-13):**
- `~/.screenmind/settings.json`: `capture_interval: 120` (max), `defer_analysis: true`
- Both pythonw autostarts (ScreenMind, WhisperLocal) relaunch at BelowNormal priority via `cmd /c start /belownormal` in HKCU Run; Startup .bat updated likewise
- Live processes set to BelowNormal
- Result: `osprivacy`/camsvc → 0% CPU; whisper ~7%; screenmind still ~2 cores while grinding the unanalyzed backlog against the dead LLM backend

**Open decision:** pause capture (Ctrl+Shift+P / `capture_paused: true`) until the Gemma model is downloaded and llama-server autostarts — analysis cannot succeed in the current state.
