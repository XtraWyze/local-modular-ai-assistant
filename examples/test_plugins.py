import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from module_manager import ModuleRegistry

# Optional: configs for modules
module_configs = {
    "hello_module": {"greeting": "Hi!"}
}

registry = ModuleRegistry()
registry.auto_discover("modules", config_map=module_configs)

print("Discovered modules:", registry.modules.keys())

# Call a function in the discovered module
result = registry.call("modules.hello_module", "say_hello", "Levi")
print(result)

# Shutdown all modules
registry.shutdown_all()
