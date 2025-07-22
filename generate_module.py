# generate_module.py
import os

MODULE_TEMPLATE = '''"""
{module_name}.py
{description}
"""

import time
from error_logger import log_error

DEFAULT_CONFIG = {default_config}

def initialize(config=None):
    try:
        # Run setup if needed
        pass
    except Exception as e:
        log_error(f"[{module_name}] Error in initialize: {{e}}")

def get_status():
    return "{module_name} loaded and ready!"

def main_function(input_data=None):
    try:
        # Main logic here
        return f"Processed input: {{input_data}}"
    except Exception as e:
        log_error(f"[{module_name}] Error in main_function: {{e}}")
        return f"Error: {{e}}"

def helper():
    pass

def shutdown():
    try:
        # Clean up resources
        pass
    except Exception as e:
        log_error(f"[{module_name}] Error in shutdown: {{e}}")

def get_info():
    return {{
        "name": "{module_name}",
        "description": "{description}",
        "functions": [
            "initialize", "get_status", "main_function", "shutdown", "get_info"
        ]
    }}

def register():
    from module_manager import ModuleRegistry
    ModuleRegistry.register("{module_name}", {{
        "initialize": initialize,
        "get_status": get_status,
        "main_function": main_function,
        "shutdown": shutdown,
        "get_info": get_info
    }})
# Optionally: register()
'''

TEST_TEMPLATE = '''# test_{module_name}.py
from modules import {module_name}

def test_main():
    result = {module_name}.main_function("test input")
    print(f"Result: {{result}}")

if __name__ == "__main__":
    test_main()
'''

CONFIG_TEMPLATE = '''{{
    // Configuration for {module_name}
    "example_setting": true
}}
'''

def main():
    print("=== New Module Generator ===")
    name = input("Module name (see examples/my_module.py for reference): ").strip()
    if not name:
        print("No name given, exiting.")
        return
    description = input("Brief description (one sentence): ").strip() or "Module for the assistant."
    default_config = "{}"
    make_test = input("Create basic test script? (y/n): ").strip().lower().startswith("y")
    make_config = input("Create basic config file? (y/n): ").strip().lower().startswith("y")

    # Module file
    module_path = os.path.join("modules", f"{name}.py")
    os.makedirs("modules", exist_ok=True)
    if os.path.exists(module_path):
        print(f"File '{module_path}' already exists! Not overwriting.")
        return
    with open(module_path, "w", encoding="utf-8") as f:
        f.write(MODULE_TEMPLATE.format(
            module_name=name,
            description=description,
            default_config=default_config
        ))
    print(f"Module template created at '{module_path}'")

    # Test script
    if make_test:
        test_dir = "tests"
        os.makedirs(test_dir, exist_ok=True)
        test_path = os.path.join(test_dir, f"test_{name}.py")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(TEST_TEMPLATE.format(module_name=name))
        print(f"Test script created at '{test_path}'")

    # Config file
    if make_config:
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, f"{name}_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(CONFIG_TEMPLATE.format(module_name=name))
        print(f"Config file created at '{config_path}'")

if __name__ == "__main__":
    main()
