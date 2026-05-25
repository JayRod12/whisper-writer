# Running whisper-writer on Fedora 42 / Python 3.13 / GNOME Wayland

These are the steps needed to get whisper-writer working on a modern Fedora
setup. The original `requirements.txt` was generated for Python 3.8–3.11 on
Windows and needs several fixes.

---

## 1. System dependencies

```bash
# FFmpeg dev libs (required to build the `av` package)
sudo dnf install ffmpeg-free-devel

# Python 3.13 dev headers (required to compile evdev, webrtcvad-wheels)
sudo dnf install python3.13-devel

# GObject / Cairo (required by audioplayer via PyGObject)
sudo dnf install gobject-introspection-devel cairo-gobject-devel

# ydotool — Wayland-native keyboard injection (pynput and wtype don't work on GNOME Wayland)
sudo dnf install ydotool

# udev rule so ydotoold can open /dev/uinput without root
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/60-uinput.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## 2. User group membership

evdev (key detection) and ydotoold (text injection) both need access to input
devices. Add your user to the `input` group and log out/in for it to take effect:

```bash
sudo usermod -aG input $USER
# then log out and back in (or: newgrp input in the current terminal only)
```

## 3. Python venv + dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install PyGObject        # must come before requirements.txt
pip install -r requirements.txt
```

> **Note:** `requirements.txt` in this fork has already been updated for Python
> 3.13. If you're starting from the upstream repo, see the package changes
> summarised at the bottom of this file.

## 4. Run

```bash
source venv/bin/activate
python run.py
```

The Qt panel will open. Click **Start** to activate the key listener, then use
`Ctrl+Shift+Space` (configurable in Settings) to start recording.

The app auto-starts `ydotoold` on launch and kills it on exit — no manual
daemon management needed.

---

## How it works on GNOME Wayland

| Layer | Solution | Why |
|---|---|---|
| Key detection | `evdev` (reads `/dev/input/event*`) | pynput needs X11 for global hotkeys |
| Text injection | `ydotool` / `ydotoold` | pynput Controller needs X11; wtype needs `zwp_virtual_keyboard_v1` which GNOME doesn't implement |
| Audio | `sounddevice` / ALSA | works as-is |

---

## Package changes vs upstream requirements.txt

The upstream file was also UTF-16 encoded (Windows artifact). This fork ships a
clean UTF-8 version with these version bumps for Python 3.13 compatibility:

| Package | Upstream | This fork |
|---|---|---|
| `ctranslate2` | 4.2.1 | 4.7.2 |
| `av` | 11.0.0 | 17.0.1 |
| `faster-whisper` | 1.0.2 | 1.1.1 |
| `onnxruntime` | 1.16.3 | 1.26.0 |
| `tokenizers` | 0.15.0 | 0.21.0 |
| `tiktoken` | 0.3.1 | 0.9.0 |
| `huggingface-hub` | 0.20.1 | 0.27.0 |
| `pydantic` | 2.7.1 | 2.10.6 |
| `pydantic_core` | 2.18.2 | 2.27.2 |
| `numpy` | 1.24.3 | 2.2.6 |
| `Pillow` | 9.5.0 | 11.2.1 |
| `aiohttp` | 3.8.4 | 3.11.12 |
| `cffi` | 1.15.1 | 1.17.1 |
| `frozenlist` | 1.3.3 | 1.5.0 |
| `multidict` | 6.0.4 | 6.4.3 |
| `yarl` | 1.9.2 | 1.18.3 |
| `regex` | 2023.5.5 | 2024.11.6 |
| `typing_extensions` | 4.11.0 | 4.12.2 |
| `webrtcvad-wheels` | 2.0.11.post1 | 2.0.14 |
| `PyQt5-sip` | 12.13.0 | 12.18.0 |
| `PyQt5-Qt5` | 5.15.2 | 5.15.19 |
| `numba` | 0.57.0 | removed (not needed by faster-whisper, incompatible with Python 3.13) |
| `llvmlite` | 0.40.0 | removed (same reason) |
