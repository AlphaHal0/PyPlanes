from ui.element import UIElement

class Text(UIElement):
    def  __init__(self, content: str = "", id: str = ""):
        super().__init__(id)
