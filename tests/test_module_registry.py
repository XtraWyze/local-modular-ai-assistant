import sys
from module_manager import ModuleRegistry


def test_auto_discover_loads_module(tmp_path, monkeypatch):
    pkg = tmp_path / "mods"
    pkg.mkdir()
    module_code = """
initialized = []
last_config = None

def initialize(config=None):
    global last_config
    initialized.append(config)
    last_config = config

def hello():
    return 'hi'
"""
    (pkg / "m1.py").write_text(module_code)
    # auto_discover should create __init__.py automatically
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = ModuleRegistry()
    registry.auto_discover("mods", config_map={"m1": {"foo": "bar"}})

    assert "mods.m1" in registry.modules
    mod = registry.modules["mods.m1"]
    assert mod.last_config == {"foo": "bar"}


def test_auto_discover_creates_init(tmp_path, monkeypatch):
    pkg = tmp_path / "mods"
    pkg.mkdir()
    (pkg / "m2.py").write_text("pass")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = ModuleRegistry()
    registry.auto_discover("mods")

    assert (pkg / "__init__.py").exists()


def test_list_descriptions(tmp_path, monkeypatch):
    pkg = tmp_path / "mods"
    pkg.mkdir()
    (pkg / "m3.py").write_text(
        "def get_description():\n    return 'demo module'\n"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop('mods', None)

    registry = ModuleRegistry()
    registry.auto_discover("mods")

    descs = registry.list_descriptions()
    assert descs == {"mods.m3": "demo module"}


def test_call_logs_errors_on_exception(monkeypatch):
    """Ensure call() logs errors and returns None on failure."""
    import types

    faulty_mod = types.ModuleType("mods.err")

    def boom():
        raise RuntimeError("boom")

    faulty_mod.boom = boom
    sys.modules["mods.err"] = faulty_mod

    registry = ModuleRegistry()
    registry.modules["mods.err"] = faulty_mod

    logged = []

    monkeypatch.setattr(
        "module_manager.log_error",
        lambda msg, context=None, level="ERROR": logged.append((msg, context)),
    )

    result = registry.call("mods.err", "boom")

    assert result is None
    assert any("boom" in msg for msg, _ in logged)

