# Base class for all UI elements

class UIElement:
    def __init__(self, id: str = ""):
        self.id = id

    def update(self, **kwargs): pass
