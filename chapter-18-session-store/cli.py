import click
import pprint
from database import SessionStoreTable

pp = pprint.PrettyPrinter(indent=2)


@click.group()
def cli():
    pass


@cli.command(name="create")
@click.argument("table")
def create(table):
    SessionStoreTable(table).create()


@cli.command(name="delete")
@click.argument("table")
def delete(table):
    SessionStoreTable(table).delete()


@cli.command(name="describe")
@click.argument("table")
def describe(table):
    result = SessionStoreTable(table).describe()
    pp.pprint(result)


@cli.command(name="add-token")
@click.argument("table")
@click.argument("user")
@click.option("--ttl", default=86400, help="Token time-to-live in seconds")
def add_token(table, user, ttl):
    token = SessionStoreTable(table).add_token(user, ttl)
    print(token)


@cli.command(name="get-token")
@click.argument("table")
@click.argument("token")
def get_token(table, token):
    result = SessionStoreTable(table).get_token(token)
    pp.pprint(result)


@cli.command(name="list-all")
@click.argument("table")
def list_all(table):
    result = SessionStoreTable(table).list_all()
    pp.pprint(result)


@cli.command(name="delete-token")
@click.argument("table")
@click.argument("token")
def delete_token(table, token):
    SessionStoreTable(table).delete_token(token)


@cli.command(name="delete-user-tokens")
@click.argument("table")
@click.argument("user")
def delete_user_tokens(table, user):
    SessionStoreTable(table).delete_user_tokens(user)


if __name__ == '__main__':
    cli()
