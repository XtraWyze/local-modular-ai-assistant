import planning_agent


def test_create_plan_splits_tasks():
    text = "Open browser and search cats then save results"
    plan = planning_agent.create_plan(text)
    assert plan == ["open browser", "search cats", "save results"]


def test_assign_tasks_calls_dispatch():
    tasks = ["a", "b"]
    called = []
    planning_agent.assign_tasks(tasks, called.append)
    assert called == tasks
