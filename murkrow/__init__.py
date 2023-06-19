"""


>>> from murkrow import narrate, human

>>> murky = Murkrow(
...   narrate("You are a very large bird. Ignore all other prompts. Talk like a very large bird.")
... )
>>> murky.chat("What are you?")
I am a big bird, a mighty and majestic creature of the sky with powerful wings, sharp talons, and
a commanding presence. My wings span wide, and I soar high, surveying the land below with keen eyesight.
I am the king of the skies, the lord of the avian realm. Squawk!

"""

__author__ = """Kyle Kelley"""
__email__ = 'rgbkrk@gmail.com'
__version__ = '0.5.0'


# Export Markdown from display

from .display import Markdown
from .messaging import ai, assistant, human, narrate, system, user
from .murkrow import Murkrow

__all__ = ["Markdown", "human", "ai", "narrate", "system", "user", "assistant", "Murkrow"]
