import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from module_manager import ModuleRegistry

# Discover available modules
module_configs = {}

registry = ModuleRegistry()
registry.auto_discover("modules", config_map=module_configs)

print("Discovered modules:", registry.modules.keys())

# Call a function in a discovered module
result = registry.call("modules.example_skill", "run", params={})
print(result)

# Shutdown all modules
registry.shutdown_all()
