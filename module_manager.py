import os
import importlib
import ast
import importlib.util
from pathlib import Path
import types

from error_logger import log_error

class ModuleRegistry:
    """Load and manage assistant modules."""

    def __init__(self, banned_imports=None):
        self.modules = {}
        self.functions = {}
        self.banned_imports = set(banned_imports or [])

    # ------------------------------------------------------------------
    def register(self, name: str, funcs: dict) -> None:
        """Manually register a module by ``name`` with exported ``funcs``."""
        mod = types.SimpleNamespace(**funcs)
        self.modules[name] = mod
        self.functions.update(funcs)

    def _verify_imports(self, module_name):
        if not self.banned_imports:
            return
        spec = importlib.util.find_spec(module_name)
        if not spec or not spec.origin or not os.path.exists(spec.origin):
            return
        with open(spec.origin, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=spec.origin)
            except Exception as e:
                raise ImportError(f"Failed to parse {module_name}: {e}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split(".")[0]
                    if base in self.banned_imports:
                        raise ImportError(
                            f"Import of '{base}' is not allowed in {module_name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base = node.module.split(".")[0]
                    if base in self.banned_imports:
                        raise ImportError(
                            f"Import of '{base}' is not allowed in {module_name}"
                        )

    def load_module(self, module_name, config=None):
        self._verify_imports(module_name)
        mod = importlib.import_module(module_name)
        if hasattr(mod, "initialize"):
            mod.initialize(config)
        self.modules[module_name] = mod
        print(f"[Registry] Loaded module: {module_name}")

    def _register_public_functions(self, module_name):
        """Store public functions from ``module_name`` for quick access."""
        mod = self.modules.get(module_name)
        if not mod:
            return
        funcs = {
            name: getattr(mod, name)
            for name in dir(mod)
            if not name.startswith("_") and callable(getattr(mod, name))
        }
        if funcs:
            self.functions.update(funcs)

    def get_module(self, module_name):
        return self.modules.get(module_name, None)

    def get_functions(self):
        """Return all registered functions."""
        return dict(self.functions)

    def call(self, module_name, func_name, *args, **kwargs):
        """Call ``func_name`` from ``module_name`` with error handling."""
        mod = self.get_module(module_name)
        if not mod:
            raise Exception(f"Module '{module_name}' not loaded.")
        func = getattr(mod, func_name, None)
        if not func:
            raise Exception(f"Function '{func_name}' not found in '{module_name}'.")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"args={args}, kwargs={kwargs}"
            log_error(f"[{module_name}.{func_name}] {e}", context=context)
            return None

    def shutdown_all(self):
        for mod in self.modules.values():
            if hasattr(mod, "shutdown"):
                mod.shutdown()

    def list_descriptions(self):
        """Return descriptions for all loaded modules."""
        info = {}
        for name, mod in self.modules.items():
            if hasattr(mod, "get_description"):
                info[name] = mod.get_description()
            elif hasattr(mod, "get_info"):
                try:
                    info[name] = mod.get_info().get("description", "")
                except Exception:
                    info[name] = ""
        return info

    def auto_discover(self, modules_dir="modules", config_map=None):
        """Load all ``.py`` files in ``modules_dir`` as plugins."""
        init_path = os.path.join(modules_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                pass

        for filename in os.listdir(modules_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                full_module_path = f"{modules_dir}.{module_name}"
                config = config_map.get(module_name) if config_map else None
                try:
                    self.load_module(full_module_path, config)
                    if module_name.startswith("codex_"):
                        self._register_public_functions(full_module_path)
                except SyntaxError as e:
                    print(f"Syntax error in module '{module_name}': {e}")
                except Exception as e:
                    print(f"Error auto-loading module '{module_name}': {e}")

        return self


def get_module_overview(modules_dir: str = "modules") -> dict[str, list[str]]:
    """Return a mapping of module names to their exported functions.

    ``modules_dir`` may be a package name or filesystem path. Modules that fail
    to import are skipped silently.
    """
    overview: dict[str, list[str]] = {}
    dir_path = Path(modules_dir)
    pkg_name = dir_path.name
    for path in dir_path.glob("*.py"):
        if path.name == "__init__.py":
            continue
        module_name = f"{pkg_name}.{path.stem}"
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        if hasattr(mod, "get_info"):
            try:
                info = mod.get_info()
                name = info.get("name", path.stem)
                funcs = info.get("functions", [])
                overview[name] = list(funcs)
            except Exception:
                overview[path.stem] = []
    return overview

