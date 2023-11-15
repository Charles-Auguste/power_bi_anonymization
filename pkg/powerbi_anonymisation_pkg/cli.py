import click


@click.group()
def cli():
    pass


@click.command("run")
def run():
    return None


cli.add_command(run)

if __name__ == "__main__":
    cli()
