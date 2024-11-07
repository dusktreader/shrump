import typer
import uvicorn


def dev_server(
    port: int = typer.Option(5000, help="The port where the server should listen"),
    log_level: str = typer.Option("DEBUG", help="The level to log uvicorn output"),
):
    """
    Start a development server locally.
    """
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=log_level.lower(),
    )
