# Base class for all UI elements

class UIElement:
    def __init__(self, id: str = ""):
        self.id = id
        self.listen_for_events = False

    def update(self, **kwargs): pass
