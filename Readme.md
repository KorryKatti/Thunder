# Thunder

![Thunder](https://raw.githubusercontent.com/dynobo/lmdiag/master/badge.png)

**A modern desktop app launcher for Python programs on GitHub.**

Paste a GitHub URL. Thunder downloads, installs, and launches it — with its own virtual environment, no setup required.

## Install

```bash
git clone https://github.com/korrykatti/thunder.git && cd thunder && bun install && wails dev
```

**Binary releases coming soon.**

## What it does

- Paste any GitHub URL containing a Python app
- Thunder detects the project structure (pyproject.toml, requirements.txt, etc.)
- Downloads the repo, creates a venv with [uv](https://github.com/astral-sh/uv), installs dependencies
- Launches the app — GUI apps open directly, CLI apps open in a terminal
- Manage all your installed apps from the Library

## Requirements

- Python 3.x
- [uv](https://github.com/astral-sh/uv) (Thunder can install it for you)
- [Bun](https://bun.sh) (for frontend)
- [Wails](https://wails.io/) (for building/running)
- git (for update checking)

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript (Vite)
- **Backend**: Go ([Wails](https://wails.io/))
- **Package management**: [uv](https://github.com/astral-sh/uv)
- **Theme**: GitHub Dark

## License

MIT

## Credit

Born from [this Reddit post](https://www.reddit.com/r/github/comments/1at9br4/) — the frustration of non-developers trying to use GitHub.

> "I DONT GIVE A FUCK ABOUT THE FUCKING CODE! i just want to download this stupid fucking application and use it. WHY IS THERE CODE???"
> — u/automatic_purpose_

Thunder exists so nobody has to feel this way again.
