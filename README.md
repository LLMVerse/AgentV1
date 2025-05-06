# LLMVerse Agent & Backend

Welcome!  
To run the LLMVerse Agent and Backend locally, **you must download both the backend and the agent**.  
This guide will walk you through all required installations, setup, and troubleshooting.

---

## 1. Required Installations

Before you begin, make sure you have **all** of the following installed:

- **Python 3.7+**  
  [Download Python](https://www.python.org/downloads/release/python-3130/)  
  (Be sure to check "Add Python to PATH" during installation!)

- **Git**  
  [Download Git](https://git-scm.com/downloads)

- **(Optional) NVIDIA GPU** and drivers for real GPU detection  
  [NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx)


## 2. Download the Repository (Backend & Agent)

You need to download the **entire repository**, which contains both the backend and agent code.

**Option 1: Using Git (recommended, all branches and history)**

Open a terminal in the folder where you want to download the project, then run:

```bash
git clone https://github.com/LLMVerse/AgentV1.git
```

This will create a folder named `AgentV1` in your current directory and download **all branches and folders**.

To see available branches:
```bash
cd AgentV1
git branch -a
```

To switch to a different branch (for example, `dev`):
```bash
git checkout dev
```

**Option 2: Download ZIP (only downloads the default branch)**

- Go to [https://github.com/LLMVerse/AgentV1](https://github.com/LLMVerse/AgentV1)
- Click the green "Code" button, then "Download ZIP".
- Extract the ZIP file. This will create a folder named `AgentV1-main` (or similar).
- **Note:** This method only gives you the default branch (usually `main`). If you need other branches, use the Git method above.

**Change directory into the project folder:**

If you used git, run:
```bash
cd AgentV1
```
If you downloaded and extracted the ZIP, run:
```bash
cd AgentV1-main
```
or use the actual folder name if different.

You can use `ls` (Linux/Mac) or `dir` (Windows) to list folders and verify the correct name.

---

## 3. Folder Structure

After downloading, your folder structure will look like this:

```
AgentV1-main/         # or AgentV1/ depending on your download method
├── agent/
│   └── agent_v1.py
├── backend/
│   ├── backend_api.py
│   └── requirements.txt
├── requirements.txt
└── README.md
```

---

## 4. Install Python & pip

**Check if Python is installed:**

Open a terminal (Command Prompt, PowerShell, or Terminal) and run:
```bash
python --version
```
or
```bash
python3 --version
```

If you see a version number (e.g., `Python 3.11.4`), Python is installed.  
If you see an error like `'python' is not recognized as an internal or external command`, you need to install Python.

**To install Python:**

- Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Download the latest Python 3.x installer for your OS.
- Run the installer.
- **IMPORTANT:** On the first screen, check the box that says **"Add Python to PATH"** before clicking "Install Now".
- Complete the installation.

After installing, close and reopen your terminal, then run:
```bash
python --version
```
You should now see the Python version.

---

## 5. Troubleshooting: Python Not in PATH

If you forgot to check "Add Python to PATH" during installation, you'll see errors like:

```
'python' is not recognized as an internal or external command...
```
or (in French):
```
Python est introuvable; exécutez sans arguments à installer à partir du Microsoft Store...
```

**How to fix:**

1. **Find your Python install folder:**
   - Open File Explorer.
   - In the address bar, type `%LOCALAPPDATA%` and press Enter. This will take you to your `AppData\Local` folder.
   - Navigate to `Programs\Python\Python3xx` (e.g., `Python311` for Python 3.11).
   - You should see `python.exe` in this folder.

2. **Find the Scripts subfolder:**
   - Inside the same `Python3xx` folder, open the `Scripts` folder.

3. **Add both folders to your PATH:**
   - Open Start, search for "Environment Variables", and open it.
   - Click "Environment Variables..." at the bottom.
   - Under "User variables", select `Path` and click "Edit".
   - Click "New" and add both full paths:
     - Example: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
     - Example: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
   - Click OK to close all dialogs.

4. **Close and reopen your terminal**, then run:
```bash
python --version
pip --version
```
Both should now work.

If you still have issues, restart your computer or try running `py --version`.

---

## 6. Install Git

Check if Git is installed:
```bash
git --version
```
If not, download and install from [https://git-scm.com/downloads](https://git-scm.com/downloads).

---

## 7. Install Python dependencies

From the project root (the folder containing `requirements.txt`), run:
```bash
python -m pip install -r requirements.txt
```
This will install all dependencies for both the agent and backend.

If you get an error like `No module named pip`, see the troubleshooting above or download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run:
```bash
python get-pip.py
```

---

## 8. Start the Backend API

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

## 9. Run the Agent Console

Open a new terminal in the same folder and run:

```bash
python agent/agent_v1.py
```

---

## 10. Using the Agent Console

- You will see a list of detected GPUs (real or mock).
- You will see:  
  `Current Solana wallet payout address: (none)`

**To test:**
1. Choose `1` to open Settings.
2. Choose `1` again to enter your Solana wallet payout address.
3. Choose `2` to select which GPUs to share and set the % power for each.
   - Enter indices (e.g., `0,1`).
   - Enter the % power for each GPU when prompted.
4. Choose `4` to go back to the main menu.
5. Choose `2` to confirm and make GPUs available.
   - Review the summary.
   - Type `y` to confirm.

- The agent will send your wallet and GPU info to the backend.
- The backend will register your agent and create a CPP.
- You’ll see a message like: `CPP created! CPP ID: ...`
- Your GPUs are now "available" to the LLMVerse CPP (simulated).

---

## 11. (Optional) View Backend Data

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to view and test backend endpoints (`/nodes`, `/cpps`).

---

## 12. Troubleshooting

- If `pip` or `python` are not recognized, repeat the PATH steps above.
- If you get connection errors, make sure the backend is running and accessible at `http://127.0.0.1:8000`.
- If you do not have an NVIDIA GPU or `pynvml` is not installed, the agent will use mock GPU data.
- If you get permission errors, try running your terminal as administrator.

---

## 13. Stopping

- Press `Ctrl+C` in the agent terminal to exit.
- Press `Ctrl+C` in the backend terminal to stop the backend.

---

## License

MIT License

---
