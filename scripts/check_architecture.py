from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "muwajjih"
RULES = {
    "domain": ("muwajjih.api", "muwajjih.adapters", "fastapi", "redis", "sklearn"),
    "service": ("muwajjih.api", "muwajjih.adapters", "fastapi", "redis", "sklearn"),
}

violations: list[str] = []
for layer, forbidden in RULES.items():
    layer_root = ROOT / layer
    for path in layer_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported = None
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module]
            if not imported:
                continue
            for module in imported:
                if any(module == item or module.startswith(item + ".") for item in forbidden):
                    violations.append(f"{path}:{node.lineno}: {module}")

if violations:
    print("Architecture violations:")
    print("\n".join(violations))
    raise SystemExit(1)
print("architecture_check_ok")
