import ast
import subprocess
import sys
from pathlib import Path

MODULES_DIR = Path(__file__).parent / "modules"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"


def parse_requirements(path: Path) -> list[str]:
    """Return REQUIREMENTS list from a module file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception:
        return []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "REQUIREMENTS":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        items = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                items.append(elt.value)
                        return items
    return []


def collect_module_requirements(mod_dir: Path) -> set[str]:
    """Collect all REQUIREMENTS from modules in ``mod_dir``."""
    reqs: set[str] = set()
    for file in mod_dir.glob("*.py"):
        reqs.update(parse_requirements(file))
    return reqs


def read_requirements_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def write_requirements_file(path: Path, reqs: list[str]) -> None:
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for dep in reqs:
            f.write(dep + "\n")
    tmp.replace(path)


def install_new_packages(packages: list[str]) -> None:
    if not packages:
        return
    cmd = [sys.executable, "-m", "pip", "install", *packages]
    print("Installing:", " ".join(packages))
    subprocess.check_call(cmd)


def main() -> None:
    module_reqs = collect_module_requirements(MODULES_DIR)
    existing = read_requirements_file(REQUIREMENTS_FILE)
    missing = sorted(module_reqs - set(existing))

    if missing:
        print("Adding new dependencies:", ", ".join(missing))
        all_reqs = existing + missing
        write_requirements_file(REQUIREMENTS_FILE, all_reqs)
        install_new_packages(missing)
    else:
        print("No new dependencies found.")


if __name__ == "__main__":
    main()
