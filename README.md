# LLMVerse Agent & Backend

This guide helps you run the LLMVerse Agent and Backend locally.

---

## Quick Start

### 1. Requirements

- [Python 3.7+](https://www.python.org/downloads/) (check "Add Python to PATH" during install)
- [Git](https://git-scm.com/downloads)
- (Optional) [NVIDIA GPU Drivers](https://www.nvidia.com/Download/index.aspx)

### 2. Download the Code

**With Git (recommended):**
```bash
git clone https://github.com/LLMVerse/AgentV1.git
cd AgentV1
```
**Or Download ZIP:**  
Download and extract from GitHub, then `cd` into the folder.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the Backend

```bash
uvicorn backend.backend_api:app --reload
```
- The backend runs at the address shown in your terminal (default: `http://127.0.0.1:8000`).
- The API UI is at `/docs` (e.g., `http://127.0.0.1:8000/docs`).

### 5. Run the Agent

Open a new terminal in the same folder:
```bash
python agent/agent_v1.py
```

---

## Notes & Troubleshooting

- If `python` or `pip` are not recognized, add Python to your PATH (see [Python docs](https://docs.python.org/3/using/windows.html#configuring-python)).
- If you see a 404 at `/`, use `/docs` for the API UI.
- Set your Solana wallet and select GPUs in the agent before updating CPP settings.
- To stop, press `Ctrl+C` in each terminal.

---


MIT License
