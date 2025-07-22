import time

import remote_agent


def test_send_and_receive_command():
    received = []
    srv = remote_agent.RemoteServer(callback=received.append)
    srv.start()
    assert remote_agent.send_command("localhost", srv.port, "hello") is True
    # give server a moment to process
    for _ in range(20):
        if received:
            break
        time.sleep(0.05)
    srv.shutdown()
    assert received == ["hello"]
