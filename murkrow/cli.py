"""Console script for murkrow."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("murkrow")
    click.echo("=" * len("murkrow"))
    click.echo("Markdown for LLMs")


if __name__ == "__main__":
    main()  # pragma: no cover
