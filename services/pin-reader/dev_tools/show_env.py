import json

import typer
from snick import conjoin

from api.config import settings

app = typer.Typer()


@app.command()
def show_env(use_json: bool = typer.Option(False, "--json", help="Dump as JSON")):
    """
    Print out the current environment settings.
    """
    if use_json:
        output = json.dumps(settings.dict())
    else:
        output = conjoin(
            "Jobbergate settings:",
            *[f"{k}: {v}" for (k, v) in settings.dict().items()],
            join_str="\n  "
        )
    print(output)
