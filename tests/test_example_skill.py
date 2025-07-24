from modules import example_skill


def test_run():
    assert example_skill.run({}) == "hello from example"
