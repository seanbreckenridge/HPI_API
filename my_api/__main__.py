import sys

import click

from .discovery import iter_modules, iter_functions


@click.group()
def main() -> None:
    pass

@main.command()
def server() -> None:
    iter_modules()

@main.command()
@click.option("--functions", required=False, default=False, is_flag=True)
def list_modules(functions: bool) -> None:
    for mod in iter_modules():
        click.echo(mod.name)
        if functions:
            for (_mod, func) in iter_functions(mod):
                click.echo(f"- {func}")

if __name__ == "__main__":
    main()

