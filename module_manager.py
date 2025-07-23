import os
import importlib
import ast
import importlib.util

class ModuleRegistry:
    def __init__(self, banned_imports=None):
        self.modules = {}
        self.banned_imports = set(banned_imports or [])

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

    def get_module(self, module_name):
        return self.modules.get(module_name, None)

    def call(self, module_name, func_name, *args, **kwargs):
        mod = self.get_module(module_name)
        if not mod:
            raise Exception(f"Module '{module_name}' not loaded.")
        func = getattr(mod, func_name, None)
        if not func:
            raise Exception(f"Function '{func_name}' not found in '{module_name}'.")
        return func(*args, **kwargs)

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
                except Exception as e:
                    print(f"Error auto-loading module '{module_name}': {e}")

        return self
