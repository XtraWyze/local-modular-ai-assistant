import android_cli_assistant as aca

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    KIVY_AVAILABLE = True
except Exception:  # pragma: no cover - Kivy may not be installed
    KIVY_AVAILABLE = False
    App = object  # type: ignore
    BoxLayout = object  # type: ignore
    Label = object  # type: ignore
    TextInput = object  # type: ignore


class AssistantLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.memory = aca.load_memory()
        self.output = Label(size_hint_y=0.8)
        self.input = TextInput(hint_text="Type a command", multiline=False)
        self.input.bind(on_text_validate=self.on_enter)
        self.add_widget(self.output)
        self.add_widget(self.input)

    def on_enter(self, _instance) -> None:
        text = self.input.text
        self.input.text = ""
        response = aca.handle_input(text, self.memory)
        if response is None:
            App.get_running_app().stop()
        else:
            self.output.text = str(response)
            aca.save_memory(self.memory)


class AndroidAssistantApp(App):
    def build(self) -> BoxLayout:
        return AssistantLayout()


if __name__ == "__main__":
    if not KIVY_AVAILABLE:
        raise SystemExit("Kivy must be installed to run this app")
    AndroidAssistantApp().run()
