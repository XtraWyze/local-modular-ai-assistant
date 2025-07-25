class DummyText:
    def __init__(self):
        self.text = ""
        self.state = None
    def config(self, *, state):
        self.state = state
    def delete(self, *_):
        self.text = ""
    def insert(self, *_args):
        self.text += _args[1]


def run_learning(prompts, widget, update_phrases=False):
    widget.config(state="normal")
    widget.delete("1.0", None)
    for p in prompts:
        widget.insert("end", f"heard {p}\n")
    if update_phrases and len(prompts) >= 2:
        widget.insert("end", f"wake:{prompts[0]}\n")
        widget.insert("end", f"sleep:{prompts[1]}\n")
    widget.config(state="disabled")


def test_run_learning_basic():
    w = DummyText()
    run_learning(["a", "b"], w, update_phrases=True)
    assert "heard a" in w.text and "wake:a" in w.text
