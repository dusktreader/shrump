import typer

from dev_tools import dev_server, show_env

app = typer.Typer()
app.command(name="dev-server")(dev_server.dev_server)
app.command(name="show-env")(show_env.show_env)


if __name__ == "__main__":
    app()
