import click

from flask import Flask

from .discovery import iter_modules, iter_functions
from .server import generate_server


@click.group()
def main() -> None:
    pass


@main.command()
@click.option("--print-routes", required=False, default=False, is_flag=True)
def server(print_routes: bool) -> None:
    app: Flask = generate_server()
    if print_routes:
        for rule in app.url_map.iter_rules():
            click.echo(str(rule))
    else:
        app.run(host="0.0.0.0", port="5050")


@main.command()
@click.option("--functions", required=False, default=False, is_flag=True)
def list_modules(functions: bool) -> None:
    for mod in iter_modules():
        click.echo(mod.name)
        if functions:
            for (fname, func) in iter_functions(mod):
                click.echo("- {}".format(fname))


if __name__ == "__main__":
    main()
