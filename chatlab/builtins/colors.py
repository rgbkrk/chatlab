"""Let models pick and show color palettes to you."""
import hashlib
from typing import List, Optional
from pydantic import BaseModel, validator, Field

from IPython.display import display


class Palette(BaseModel):
    """A palette of colors for the user to see."""

    colors: List[str] = Field(..., description="A list of CSS colors to display.")
    name: Optional[str] = None

    @validator("colors", each_item=True)
    def check_color_validity(cls, v):
        if not isinstance(v, str):
            raise ValueError("Each color must be a string representation of a CSS color.")
        if not all(c.isalnum() or c in "#.,()% " for c in v):
            raise ValueError(
                "Color contains invalid characters. Only alphanumeric and CSS color specific characters are allowed."
            )
        return v

    def _repr_html_(self):
        html = "<div>"
        for color in self.colors:
            html += f'<div style="background-color:{color}; width:50px; height:50px; display:inline-block;"></div>'
        html += "</div>"

        return html

    def __repr__(self):
        """Returns a string representation of the palette."""
        return f"Palette({self.colors}, {self.name})"


def _generate_palette_name(colors: List[str]) -> str:
    hash_object = hashlib.sha1("".join(colors).encode())
    return f"palette-{hash_object.hexdigest()}"


def show_colors(colors: List[str]):
    """Shows a list of CSS colors for the user in their notebook."""
    palette = Palette(colors=colors)

    display(palette)
    return "Displayed colors for user."
