"""Color hacking in the notebook.

This module exposes a function that will store """
import hashlib
from typing import Dict, List, Optional

from IPython.display import display


class Palette:
    """A palette of colors for the user to see."""

    def __init__(self, colors: List[str], name: Optional[str]):
        """Creates a palette of colors for the user to see."""
        self.colors = colors
        self.name = name

    @property
    def colors(self):
        """Returns the colors in the palette."""
        return self._colors

    @colors.setter
    def colors(self, colors: List[str]):
        self._colors = colors
        self.html = "<div>"
        for color in colors:
            self.html += f'<div style="background-color:{color}; width:50px; height:50px; display:inline-block;"></div>'
        self.html += "</div>"

    def _repr_html_(self):
        return self.html

    def __repr__(self):
        """Returns a string representation of the palette."""
        return f"Palette({self.colors}, {self.name})"


palettes: Dict[str, Palette] = {}


def _generate_palette_name(colors: List[str]) -> str:
    hash_object = hashlib.sha1("".join(colors).encode())
    return f"palette-{hash_object.hexdigest()}"


def show_colors(colors: List[str], store_as: Optional[str]):
    """Shows a list of CSS colors for the user in their notebook."""
    global palettes

    if store_as is None:
        store_as = _generate_palette_name(colors)

    palette = Palette(colors, store_as)
    palettes[store_as] = palette

    display(palette)
    return f"Displayed colors for user and stored as `palettes['{store_as}']`."
