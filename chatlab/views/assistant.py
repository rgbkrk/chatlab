from spork import Markdown

from ..messaging import assistant

class AssistantMessageView(Markdown):
    content: str= ""
    finished: bool = False
    has_displayed: bool = False

    def get_message(self):
        return assistant(content=self.content)

    def display(self):
        super().display()
        self.has_displayed = True

    def display_once(self):
        if not self.has_displayed:
            self.display()


