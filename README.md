# DuoAI

A Windows desktop workspace where Claude and ChatGPT collaborate on projects, plans, code and reviews.

## Run from source

- Python 3.11
- Windows 10/11 (64-bit)
- Install dependencies: `python -m pip install -r requirements.txt`
- Start: `python main.py`

Sign in with each provider's API key. Keys are stored in the operating system credential vault through Python Keyring; DuoAI does not fall back to plaintext key files. You can also use `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` environment variables.

## Features

- Claude and OpenAI provider/model selection
- AI prompt improvement, multi-agent task planning and sequential execution
- User-approved shared memory suggestions, plus a manually editable memory panel
- Project history and code export into isolated project workspaces
- Image, PDF, DOCX and text attachments (15 MB per-file limit)
- Bounded microphone capture and automatic temporary-audio cleanup
- Dark desktop interface

## Data and privacy

Projects, configuration and shared memory are stored locally under `~/.duoai`. Provider keys are stored in the OS credential manager. Memory suggestions are never written until you approve them. Do not attach secrets or confidential documents unless you are comfortable sending their contents to the selected AI provider.

## Tests

`pytest -q`

## Build the Windows installer

The repository's GitHub Actions workflow builds a PyInstaller application bundle and packages it into a per-user `DuoAI-Setup-1.0.0.exe` using Inno Setup. Push a version tag such as `v1.0.0` to attach the installer to a GitHub Release. The workflow also publishes the installer as a downloadable build artifact.

For a local build on Windows, install the pinned requirements and Inno Setup, then run:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --name DuoAI --collect-all PySide6 --collect-all shiboken6 --collect-all anthropic --collect-all openai --hidden-import keyring.backends.Windows --hidden-import sounddevice --hidden-import numpy --hidden-import pypdf --hidden-import docx main.py
& "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe" installer.iss
```
