# NOTE: This file contains sensitive configuration.
# The fee holder wallet (FEEPOOL_WALLET) and its private key are set as placeholders.
# You MUST replace FEEPOOL_WALLET and FEEPOOL_PRIVATE_KEY with your project's actual Solana wallet address and private key.
# The private key is required for the script to send fees from the holder's wallet and distribute them to contributors.
# DO NOT commit your real private key to version control or share it publicly.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from enum import Enum

app = FastAPI()

NODES = {}
CPPS = {}

class GPUInfo(BaseModel):
    index: int
    name: str
    memory_gb: int
    frequency: str
    percent: str  # Accepts int as string or "auto"

    # Accept both int and "auto" for percent
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_percent

    @classmethod
    def validate_percent(cls, v):
        if isinstance(v, dict):
            v = v.get("percent", None)
        if v == "auto":
            return v
        try:
            iv = int(v)
            if 1 <= iv <= 100:
                return iv
        except Exception:
            pass
        raise ValueError("percent must be 1-100 or 'auto'")

class RegisterRequest(BaseModel):
    wallet: Optional[str]
    gpus: List[GPUInfo]

class CPPType(str, Enum):
    bundled = "bundled"
    isolated = "isolated"

class Contributor(BaseModel):
    node_id: str
    gpu: GPUInfo
    ram_contributed: int

class CPP(BaseModel):
    cpp_id: str
    cpp_type: CPPType
    contributors: List[Contributor]
    total_ram: int
    target_ram: int

ALLOWED_BUNDLED_RAM_SIZES = [100, 200, 500]

class CPPCreateRequest(BaseModel):
    node_id: str
    gpus: List[GPUInfo]
    cpp_type: CPPType = CPPType.isolated
    target_ram: Optional[int] = None  # Only for bundled

@app.post("/register_agent")
def register_agent(req: RegisterRequest):
    node_id = str(uuid.uuid4())
    NODES[node_id] = {
        "wallet": req.wallet,
        "gpus": req.gpus
    }
    return {"node_id": node_id, "status": "registered"}

@app.post("/create_cpp")
def create_cpp(req: CPPCreateRequest):
    if req.cpp_type == CPPType.isolated:
        # Each GPU gets its own isolated pool
        cpp_ids = []
        for gpu in req.gpus:
            cpp_id = str(uuid.uuid4())
            contributor = Contributor(
                node_id=req.node_id,
                gpu=gpu,
                ram_contributed=gpu.memory_gb
            )
            cpp = CPP(
                cpp_id=cpp_id,
                cpp_type=CPPType.isolated,
                contributors=[contributor],
                total_ram=gpu.memory_gb,
                target_ram=gpu.memory_gb
            )
            CPPS[cpp_id] = cpp.dict()
            cpp_ids.append(cpp_id)
        return {"cpp_ids": cpp_ids, "status": "isolated_cpp_created"}
    elif req.cpp_type == CPPType.bundled:
        # Only allow predefined pool sizes
        if req.target_ram not in ALLOWED_BUNDLED_RAM_SIZES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid pool size. Allowed bundled pool sizes: {ALLOWED_BUNDLED_RAM_SIZES} GB"
            )
        target_ram = req.target_ram
        # Try to find an open bundled pool of the requested size
        for cpp in CPPS.values():
            if (
                cpp["cpp_type"] == CPPType.bundled
                and cpp["target_ram"] == target_ram
                and cpp["total_ram"] < cpp["target_ram"]
            ):
                # Add as contributor if not already
                for gpu in req.gpus:
                    ram = gpu.memory_gb
                    contributor = Contributor(
                        node_id=req.node_id,
                        gpu=gpu,
                        ram_contributed=ram
                    )
                    cpp["contributors"].append(contributor.dict())
                    cpp["total_ram"] += ram
                is_full = cpp["total_ram"] >= cpp["target_ram"]
                return {
                    "cpp_id": cpp["cpp_id"],
                    "status": "bundled_cpp_joined",
                    "is_full": is_full,
                    "total_ram": cpp["total_ram"],
                    "target_ram": cpp["target_ram"]
                }
        # No open pool, create new
        cpp_id = str(uuid.uuid4())
        contributors = []
        total_ram = 0
        for gpu in req.gpus:
            ram = gpu.memory_gb
            contributor = Contributor(
                node_id=req.node_id,
                gpu=gpu,
                ram_contributed=ram
            )
            contributors.append(contributor)
            total_ram += ram
        cpp = CPP(
            cpp_id=cpp_id,
            cpp_type=CPPType.bundled,
            contributors=contributors,
            total_ram=total_ram,
            target_ram=target_ram
        )
        CPPS[cpp_id] = cpp.dict()
        is_full = total_ram >= target_ram
        return {
            "cpp_id": cpp_id,
            "status": "bundled_cpp_created",
            "is_full": is_full,
            "total_ram": total_ram,
            "target_ram": target_ram
        }
    else:
        raise HTTPException(status_code=400, detail="Unknown CPP type")

@app.get("/cpps")
def list_cpp():
    return CPPS

@app.get("/nodes")
def list_nodes():
    return NODES

# Placeholder: Replace with your project's Solana wallet address and private key for the feepool! These placeholders will be replaced with actual values in the production environment and should not be hardcoded in the codebase as they contain sensitive information.
FEEPOOL_WALLET = "REPLACE_WITH_YOUR_PROJECT_SOLANA_WALLET"
FEEPOOL_PRIVATE_KEY = "REPLACE_WITH_YOUR_PROJECT_SOLANA_PRIVATE_KEY"

def get_total_contributions():
    """Return a dict mapping node_id to total RAM contributed across all pools."""
    contributions = {}
    for cpp in CPPS.values():
        for contributor in cpp["contributors"]:
            node_id = contributor["node_id"]
            ram = contributor["ram_contributed"]
            contributions[node_id] = contributions.get(node_id, 0) + ram
    return contributions

def distribute_fees(total_fee_amount):
    """
    Distribute total_fee_amount (in lamports or SOL) from the feepool wallet
    to all contributors, proportionally to their RAM contribution.
    This should be run on the third of each month.

    NOTE: This function is a stub. You must implement Solana transfer logic using
    FEEPOOL_WALLET and FEEPOOL_PRIVATE_KEY. Never commit your real private key to public repos.
    """
    contributions = get_total_contributions()
    total_ram = sum(contributions.values())
    if total_ram == 0:
        return {"status": "no_contributions"}
    payouts = {}
    for node_id, ram in contributions.items():
        node = NODES.get(node_id)
        wallet = node["wallet"] if node else None
        if not wallet:
            continue
        share = ram / total_ram
        payout = int(total_fee_amount * share)
        payouts[wallet] = payout
        # Here you would send payout from FEEPOOL_WALLET to wallet using FEEPOOL_PRIVATE_KEY
        # Example: solana_transfer(FEEPOOL_WALLET, FEEPOOL_PRIVATE_KEY, wallet, payout)
    return {
        "status": "distributed",
        "total_fee": total_fee_amount,
        "payouts": payouts,
        "feepool_wallet": FEEPOOL_WALLET,
        "note": (
            "FEEPOOL_WALLET and FEEPOOL_PRIVATE_KEY are placeholders. "
            "Replace them with your project's Solana wallet and private key. "
            "The private key is required for fee distribution."
        )
    }
