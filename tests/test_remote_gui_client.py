import time
import remote_agent
import remote_gui_client as rgc


def test_send_remote_command():
    received = []
    srv = remote_agent.RemoteServer(callback=received.append)
    srv.start()
    try:
        ok = rgc.send_remote_command("localhost", srv.port, "hello")
        assert ok
        for _ in range(20):
            if received:
                break
            time.sleep(0.05)
    finally:
        srv.shutdown()
    assert received == ["hello"]
