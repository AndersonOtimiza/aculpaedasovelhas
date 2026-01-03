"""
Lightweight GPU sanity check for PyTorch/Transformers.
Run: python gpu_check.py
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


def check_torch() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        import torch  # type: ignore
    except Exception as e:  # pragma: no cover - defensive
        out["torch_import_error"] = str(e)
        return out

    out["torch_version"] = getattr(torch, "__version__", "unknown")
    out["cuda_available"] = bool(torch.cuda.is_available())
    out["cuda_visible_devices"] = None

    try:
        import os

        out["cuda_visible_devices"] = os.environ.get("CUDA_VISIBLE_DEVICES")
    except Exception:
        pass

    if out["cuda_available"]:
        try:
            dev_id = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(dev_id)
            out["device_name"] = props.name
            out["compute_capability"] = f"{props.major}.{props.minor}"
            out["total_mem_gb"] = round(props.total_memory / (1024 ** 3), 2)
        except Exception as e:
            out["cuda_info_error"] = str(e)

        try:
            # Small tensor op on GPU to validate compute
            x = torch.randn(512, device="cuda")
            y = torch.relu(x).mean().item()
            out["sample_tensor_mean"] = y
        except Exception as e:  # pragma: no cover
            out["cuda_compute_error"] = str(e)
    return out


def check_transformers() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        import transformers  # type: ignore
    except Exception as e:  # pragma: no cover
        out["transformers_import_error"] = str(e)
        return out

    out["transformers_version"] = getattr(transformers, "__version__", "unknown")
    return out


def main() -> int:
    report = {
        "torch": check_torch(),
        "transformers": check_transformers(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
