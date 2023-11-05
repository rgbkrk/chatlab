"""Stylized representation of a Chat Function Call as we dance with the LLM."""

from typing import Optional

from vdom import details, div, span, style, summary

# Palette used here is https://colorhunt.co/palette/27374d526d829db2bfdde6ed
colors = {
    "darkest": "#27374D",
    "dark": "#526D82",
    "light": "#9DB2BF",
    "lightest": "#DDE6ED",
    "ultralight": "#F7F9FA",
    # Named variants (not great names...)
    "Japanese Indigo": "#27374D",
    "Approximate Arapawa": "#526D82",
    "Light Slate": "#9DB2BF",
    "Pattens Blue": "#DDE6ED",
    # ChatLab Colors
    "Charcoal": "#2B4155",
    "Lapis Lazuli": "#3C5B79",
    "UCLA Blue": "#527498",
    "Redwood": "#A04446",
    "Sunset": "#EFCF99",
}


def function_logo():
    """Styled 𝑓 logo component for use in the chat function component."""
    return span("𝑓", style=dict(color=colors["light"], paddingRight="5px", paddingLeft="5px"))


def function_verbage(state: str):
    """Simple styled state component."""
    return span(
        state,
        style=dict(color=colors["darkest"], paddingRight="5px", paddingLeft="5px"),
    )


def inline_pre(text: str):
    """A simple preformatted monospace component that works in all Jupyter frontends."""
    return span(text, style=dict(unicodeBidi="embed", fontFamily="monospace", whiteSpace="pre"))


def raw_function_interface_heading(text: str):
    """Display Input: or Output: headings for the chat function interface."""
    return div(
        text,
        style=dict(
            color=colors["darkest"],
            fontWeight="500",
            marginBottom="5px",
        ),
    )


def raw_function_interface(text: str):
    """For inputs and outputs of the chat function interface."""
    return div(
        text,
        style=dict(
            background=colors["ultralight"],
            color=colors["darkest"],
            padding="10px",
            marginBottom="10px",
            unicodeBidi="embed",
            fontFamily="monospace",
            whiteSpace="pre",
            overflowX="auto",
        ),
    )


def ChatFunctionComponent(
    name: str,
    verbage: str,
    input: Optional[str] = None,
    output: Optional[str] = None,
    finished: bool = False,
):
    """A component for displaying a chat function's state and input/output."""
    input_element = div()
    if input is not None:
        input = input.strip()
        input_element = div(raw_function_interface_heading("Input:"), raw_function_interface(input))

    output_element = div()
    if output is not None:
        output = output.strip()
        output_element = div(
            raw_function_interface_heading("Output:"),
            raw_function_interface(output),
        )

    return div(
        style(".chatlab-chat-details summary > *  { display: inline; color: #27374D; }"),
        details(
            summary(
                function_logo(),
                function_verbage(verbage),
                inline_pre(name),
                # If not finished, show "...", otherwise show nothing
                inline_pre("..." if not finished else ""),
                style=dict(cursor="pointer", color=colors["darkest"]),
            ),
            div(
                input_element,
                output_element,
                style=dict(
                    # Need some space above to separate from the summary
                    marginTop="10px",
                    marginLeft="10px",
                ),
            ),
            className="chatlab-chat-details",
            style=dict(
                background=colors["lightest"],
                padding=".5rem 1rem",
                borderRadius="5px",
            ),
        ),
    )
