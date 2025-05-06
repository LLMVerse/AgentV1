import sys
import time
import requests
import json
import os

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

# IMPORTANT: Change BACKEND_URL to the URL where your backend API is hosted. Our backend URL isn't public yet. On release, the files included in our AgentV1 will be updated to the correct URL to interact with our protocol.
BACKEND_URL = "http://127.0.0.1:8000"

CONFIG_FILE = "agent_config.json"

def get_gpus():
    gpus = []
    if NVML_AVAILABLE:
        count = pynvml.nvmlDeviceGetCount()
        for i in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode()
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle).total // (1024 ** 3)
            try:
                freq = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            except:
                freq = "N/A"
            gpus.append({
                "index": i,
                "name": name,
                "memory_gb": mem,
                "frequency": freq
            })
    else:
        # Mock data if NVML not available
        gpus = [
            {"index": 0, "name": "NVIDIA RTX 3080", "memory_gb": 10, "frequency": 9500},
            {"index": 1, "name": "NVIDIA GTX 1660", "memory_gb": 6, "frequency": 8000}
        ]
    return gpus

def print_status(gpus, wallet, cpp_id, selected_gpus, gpu_percents):
    print("="*44)
    print("           LLMVerse Agent V1")
    print("="*44)
    print("\nDetected GPUs:")
    for gpu in gpus:
        idx = gpu["index"]
        print(f"  [{idx}] {gpu['name']} - {gpu['memory_gb']}GB, {gpu['frequency']} MHz")
        if idx in selected_gpus:
            percent = gpu_percents.get(idx, 100)
            if percent == "auto":
                print(f"      % Power dedicated to CPP: AUTO (dynamic allocation)")
            else:
                print(f"      % Power dedicated to CPP: {percent}%")
    print("\nCurrent Solana wallet payout address:")
    print(f"  {wallet if wallet else '(none)'}")
    print("\nCPP ID currently connected:")
    print(f"  {cpp_id if cpp_id else '(none)'}")
    print("-"*44)

def save_config(wallet, selected_gpus, gpu_percents, cpp_id):
    config = {
        "wallet": wallet,
        "selected_gpus": selected_gpus,
        "gpu_percents": gpu_percents,
        "cpp_id": cpp_id
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                config = json.load(f)
                return (
                    config.get("wallet"),
                    config.get("selected_gpus", []),
                    {int(k): v for k, v in config.get("gpu_percents", {}).items()},
                    config.get("cpp_id")
                )
            except Exception:
                pass
    return None, [], {}, None

def register_agent(wallet, gpus, gpu_percents):
    payload = {
        "wallet": wallet,
        "gpus": [
            {
                "index": gpu["index"],
                "name": gpu["name"],
                "memory_gb": gpu["memory_gb"],
                "frequency": str(gpu["frequency"]),
                "percent": gpu_percents[gpu["index"]]
            }
            for gpu in gpus if gpu["index"] in gpu_percents
        ]
    }
    resp = requests.post(f"{BACKEND_URL}/register_agent", json=payload)
    resp.raise_for_status()
    return resp.json()["node_id"]

def create_cpp(node_id, gpus, gpu_percents, cpp_type="isolated", target_ram=None):
    payload = {
        "node_id": node_id,
        "gpus": [
            {
                "index": gpu["index"],
                "name": gpu["name"],
                "memory_gb": gpu["memory_gb"],
                "frequency": str(gpu["frequency"]),
                "percent": gpu_percents[gpu["index"]]
            }
            for gpu in gpus if gpu["index"] in gpu_percents
        ],
        "cpp_type": cpp_type
    }
    if cpp_type == "bundled" and target_ram:
        payload["target_ram"] = target_ram
    resp = requests.post(f"{BACKEND_URL}/create_cpp", json=payload)
    resp.raise_for_status()
    return resp.json()

def settings_menu(gpus, wallet, selected_gpus, gpu_percents):
    while True:
        print("\nSettings Menu:")
        print("  1. Change Solana wallet payout address")
        print("  2. Select GPUs and % power to dedicate to CPP")
        print("  3. Remove GPUs from pool")
        print("  4. Back to main menu")
        choice = input("Select an option: ").strip()
        if choice == "1":
            new_wallet = input("Enter new Solana wallet payout address: ").strip()
            confirm = input(f"Confirm change wallet address to '{new_wallet}'? (y/n): ").strip().lower()
            if confirm == "y":
                wallet = new_wallet
                print("Wallet address updated.")
        elif choice == "2":
            print("\nDetected GPUs:")
            for gpu in gpus:
                print(f"  [{gpu['index']}] {gpu['name']} - {gpu['memory_gb']}GB, {gpu['frequency']} MHz")
            print("Enter the slot numbers (indices) of the GPUs you want to connect to the pool.")
            indices = input("Enter GPU indices to dedicate (comma separated, e.g., 0,1,3,4): ").strip()
            try:
                available_indices = {gpu['index'] for gpu in gpus}
                selected = [int(i) for i in indices.split(",") if i.strip().isdigit()]
                invalid = [idx for idx in selected if idx not in available_indices]
                if invalid:
                    print(f"Warning: The following slot numbers are not available: {', '.join(map(str, invalid))}")
                    print("Please enter only valid GPU slot numbers as shown above.")
                    continue
                new_percents = {}
                for idx in selected:
                    while True:
                        percent = input(f"  Set % power to dedicate for GPU {idx} (1-100 or 'auto'): ").strip().lower()
                        if percent == "auto":
                            confirm = input(f"Confirm setting GPU {idx} to AUTO power allocation? (y/n): ").strip().lower()
                            if confirm == "y":
                                new_percents[idx] = "auto"
                                break
                            else:
                                print("Cancelled. Please enter again.")
                        else:
                            try:
                                percent_int = int(percent)
                                if 1 <= percent_int <= 100:
                                    confirm = input(f"Confirm dedicating {percent_int}% of GPU {idx} to CPP? (y/n): ").strip().lower()
                                    if confirm == "y":
                                        new_percents[idx] = percent_int
                                        break
                                    else:
                                        print("Cancelled. Please enter again.")
                                else:
                                    print("    Invalid percent, must be 1-100 or 'auto'.")
                            except:
                                print("    Invalid input, must be a number or 'auto'.")
                selected_gpus = selected
                gpu_percents = new_percents
                print("GPU selection and power dedication updated.")
            except Exception:
                print("Invalid input. No GPUs selected.")
                selected_gpus = []
                gpu_percents = {}
        elif choice == "3":
            if not selected_gpus:
                print("No GPUs currently dedicated to pools.")
                continue
            print("Currently dedicated GPUs:")
            for idx in selected_gpus:
                print(f"  [{idx}]")
            remove_indices = input("Enter GPU indices to remove from pool (comma separated): ").strip()
            try:
                remove_list = [int(i) for i in remove_indices.split(",") if i.strip().isdigit()]
                selected_gpus = [idx for idx in selected_gpus if idx not in remove_list]
                for idx in remove_list:
                    gpu_percents.pop(idx, None)
                print("Selected GPUs updated.")
            except Exception:
                print("Invalid input. No GPUs removed.")
        elif choice == "4":
            return wallet, selected_gpus, gpu_percents
        else:
            print("Invalid option.")

def main():
    gpus = get_gpus()
    wallet, selected_gpus, gpu_percents, cpp_id = load_config()
    node_id = None
    cpp_type = "isolated"
    target_ram = None

    ALLOWED_BUNDLED_RAM_SIZES = [100, 200, 500]

    while True:
        print_status(gpus, wallet, cpp_id, selected_gpus, gpu_percents)
        print("Options:")
        print("  1. Settings")
        print("  2. Update CPP Settings")
        print("  3. Change CPP Type (current: %s)" % (
            "Isolated" if cpp_type == "isolated" else f"Bundled ({target_ram}GB)" if target_ram else "Bundled"
        ))
        print("  4. Remove all GPUs from pool")
        print("  5. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            wallet, selected_gpus, gpu_percents = settings_menu(gpus, wallet, selected_gpus, gpu_percents)
            save_config(wallet, selected_gpus, gpu_percents, cpp_id)
        elif choice == "2":
            if not wallet or wallet.strip() == "":
                print("\nWARNING: You must set your Solana wallet payout address in Settings before updating CPP settings.")
                continue
            if not selected_gpus or not gpu_percents:
                print("\nPlease select GPUs in Settings first.")
                continue
            print("\nYou are about to connect the following GPUs to the CPP:")
            for idx in selected_gpus:
                gpu = next((g for g in gpus if g["index"] == idx), None)
                if gpu:
                    print(f"  [{idx}] {gpu['name']} - {gpu['memory_gb']}GB, {gpu['frequency']} MHz at {gpu_percents[idx]}% power")
            print(f"Wallet: {wallet}")
            print(f"CPP Type: {'Isolated' if cpp_type == 'isolated' else f'Bundled ({target_ram}GB)'}")
            if cpp_type == "bundled":
                if not target_ram:
                    print("Select bundled pool size:")
                    print("  1. 100GB RAM")
                    print("  2. 200GB RAM")
                    print("  3. 500GB RAM")
                    t = input("Enter 1, 2, or 3: ").strip()
                    if t == "1":
                        target_ram = 100
                    elif t == "2":
                        target_ram = 200
                    elif t == "3":
                        target_ram = 500
                    else:
                        print("Invalid selection. Only 100GB, 200GB, or 500GB pools are allowed.")
                        continue
            confirm = input("Confirm connection and register with backend? (y/n): ").strip().lower()
            if confirm == "y":
                try:
                    node_id = register_agent(wallet, [g for g in gpus if g["index"] in selected_gpus], gpu_percents)
                    cpp_resp = create_cpp(node_id, [g for g in gpus if g["index"] in selected_gpus], gpu_percents, cpp_type, target_ram)
                    # Confirmation message after backend response
                    print("\nBackend has received your CPP update.")
                    if cpp_type == "isolated":
                        cpp_id = cpp_resp.get("cpp_ids", [None])[0]
                        print(f"Isolated CPP connected! CPP ID: {cpp_id}")
                    else:
                        cpp_id = cpp_resp.get("cpp_id")
                        print(f"Bundled CPP joined! CPP ID: {cpp_id}")
                        print(f"Pool status: {cpp_resp['total_ram']}GB / {cpp_resp['target_ram']}GB")
                        if cpp_resp.get("is_full"):
                            print("Bundled pool is now FULL and available for jobs!")
                    save_config(wallet, selected_gpus, gpu_percents, cpp_id)
                    # Always display current CPP ID after update
                    print(f"Current CPP ID: {cpp_id}")
                except Exception as e:
                    print(f"Error communicating with backend: {e}")
                    continue
                print("\nYour GPUs are now made available to the LLMVerse CPP!")
                print("You can track real-time usage and earnings in the dashboard (coming soon).")
                print("Press Ctrl+C to exit the agent.")
                try:
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    print("\nExiting agent.")
                    sys.exit(0)
            else:
                print("Cancelled.")
        elif choice == "3":
            print("Select CPP Type:")
            print("  1. Isolated (dedicate only your GPU(s))")
            print("  2. Bundled (join a shared pool of 100GB, 200GB, or 500GB RAM)")
            t = input("Enter 1 for Isolated, or 2 for Bundled: ").strip()
            if t == "1":
                cpp_type = "isolated"
                target_ram = None
            elif t == "2":
                print("Select bundled pool size:")
                print("  1. 100GB RAM")
                print("  2. 200GB RAM")
                print("  3. 500GB RAM")
                pool_choice = input("Enter 1, 2, or 3: ").strip()
                if pool_choice == "1":
                    cpp_type = "bundled"
                    target_ram = 100
                elif pool_choice == "2":
                    cpp_type = "bundled"
                    target_ram = 200
                elif pool_choice == "3":
                    cpp_type = "bundled"
                    target_ram = 500
                else:
                    print("Invalid selection. Only 100GB, 200GB, or 500GB pools are allowed.")
                    cpp_type = "isolated"
                    target_ram = None
            else:
                print("Invalid selection.")
        elif choice == "4":
            selected_gpus = []
            gpu_percents = {}
            save_config(wallet, selected_gpus, gpu_percents, cpp_id)
            print("All GPUs removed from pool.")
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
