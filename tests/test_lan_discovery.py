import pytest
import lan_discovery


@pytest.mark.skipif(lan_discovery.Zeroconf is None, reason="zeroconf missing")
def test_advertise_and_discover():
    adv = lan_discovery.LanAdvertiser("TestService", 42424)
    adv.start()
    try:
        services = lan_discovery.discover_services(timeout=1.0)
    finally:
        adv.stop()
    assert any(port == 42424 for _addr, port in services.values())
