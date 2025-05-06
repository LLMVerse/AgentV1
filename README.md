# LLMVerse Agent & Backend

This repository lets you test the LLMVerse Agent console and backend locally. You can detect your GPUs, select the power to dedicate, set your Solana wallet payout address, and register your compute with a simulated backend locally on your machine.
Our version is slightly different from this one as it contains sensitive data.

---

## Folder Structure

```
LLMVerse/
├── agent/
│   └── agent_v1.py
├── backend/
│   ├── backend_api.py
│   └── requirements.txt
├── contracts/
│   └── FeePool.sol
└── README.md
```

---

## Prerequisites

- **Python 3.7+** (Windows, Linux, or Mac)
- (Optional) **NVIDIA GPU** and drivers for real GPU detection
- **Git** (to clone the repository)

---

## 1. Clone the Repository

```bash
git clone https://github.com/LLMVerse/AgentV1.git
cd LLMVerse
```

---

## 2. Add Python and pip to PATH (if needed)

If `python` or `pip` are not recognized in your terminal:

1. Find your Python install folder, e.g.  
   `C:\Users\your-username\AppData\Local\Programs\Python\Python311`
2. Also find the `Scripts` subfolder, e.g.  
   `C:\Users\your-username\AppData\Local\Programs\Python\Python311\Scripts`
3. Open Start, search for "Environment Variables", and open it.
4. Click "Environment Variables..." at the bottom.
5. Under "User variables", select `Path` and click "Edit".
6. Click "New" and add both folders above.
7. Click OK and restart your terminal.

Test with:
```bash
python --version
pip --version
```
Both should work.

---

## 3. If pip is missing

If you get an error like `No module named pip`:

1. Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and save it in your project folder.
2. Open a terminal in that folder and run:
   ```bash
   python get-pip.py
   ```
3. Then run:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 4. Install Python dependencies

```bash
python -m pip install -r backend/requirements.txt
python -m pip install fastapi uvicorn pydantic requests
```

---

## 5. Start the Backend API

In your project folder, run:

```bash
uvicorn backend.backend_api:app --reload
```
or, if `uvicorn` is not in your PATH:
```bash
python -m uvicorn backend.backend_api:app --reload
```

- Your local backend will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
- Leave this terminal open.

---

## 6. Run the Agent Console

Open a new terminal in the same folder and run:

```bash
python agent/agent_v1.py
```

---

## 7. Using the Agent Console

- You will see a list of detected GPUs (real or mock).
- You will see:  
  `Current Solana wallet payout address: (none)`

**To test:**
1. Choose `1` to open Settings.
2. Choose `a` to enter your Solana wallet payout address.
3. Choose `b` to select which GPUs to share and set the % power for each.
   - Enter indices (e.g., `0,1`).
   - Enter the % power for each GPU when prompted.
4. Choose `c` to go back to the main menu.
5. Choose `2` to confirm and make GPUs available.
   - Review the summary.
   - Type `y` to confirm.

- The agent will send your wallet and GPU info to the backend.
- The backend will register your agent and create a CPP.
- You’ll see a message like: `CPP created! CPP ID: ...`
- Your GPUs are now "available" to the LLMVerse CPP (simulated).

---

## 8. (Optional) View Backend Data

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to view and test backend endpoints (`/nodes`, `/cpps`).

---

## 9. Troubleshooting

- If `pip` or `python` are not recognized, repeat the PATH steps above.
- If you get connection errors, make sure the backend is running and accessible at `http://127.0.0.1:8000`.
- If you do not have an NVIDIA GPU or `pynvml` is not installed, the agent will use mock GPU data.

---

## 10. Stopping

- Press `Ctrl+C` in the agent terminal to exit.
- Press `Ctrl+C` in the backend terminal to stop the backend.

---

## License

MIT License

---
