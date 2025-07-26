import importlib


def test_learn_and_run(tmp_path):
    ml = importlib.import_module('macro_learning')
    importlib.reload(ml)
    ml.MACRO_DIR = str(tmp_path)

    cmds = iter(['one', 'two', 'three', 'demo'])
    path = ml.learn_macro(lambda: next(cmds), steps=3)
    assert path and path.exists()

    executed = []
    result = ml.run_macro('demo', lambda c: executed.append(c))
    assert 'Ran macro' in result
    assert executed == ['one', 'two', 'three']

