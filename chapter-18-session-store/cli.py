import click
import pprint
from database import SessionStoreTable

pp = pprint.PrettyPrinter(indent=2)

table_argument = click.argument("table")
user_option = click.option("--user", required=True, type=str)
token_option = click.option("--token", required=True, type=str)


@click.group()
def cli():
    pass


@cli.command(name="create-table")
@table_argument
def create_table(table):
    """
    Creates a DynamoDB table.
    """
    SessionStoreTable(table).create_table()


@cli.command(name="delete-table")
@table_argument
def delete_table(table):
    """
    Deletes a DynamoDB table.
    """
    SessionStoreTable(table).delete_table()


@cli.command(name="describe-table")
@table_argument
def describe_table(table):
    """
    Prints a description of the table.
    """
    result = SessionStoreTable(table).describe_table()
    pp.pprint(result)


@cli.command(name="add-token")
@table_argument
@user_option
@click.option("--ttl", default=86400, help="Token time-to-live in seconds")
def add_token(table, user, ttl):
    """
    Creates a session token for a user with a ttl.
    """
    token = SessionStoreTable(table).add_token(user, ttl)
    print(token)


@cli.command(name="get-token")
@table_argument
@token_option
def get_token(table, token):
    """
    Prints the result of querying a table by the token id.
    """
    result = SessionStoreTable(table).get_token(token)
    pp.pprint(result)


@cli.command(name="list-all")
@table_argument
def list_all(table):
    """
    Prints the result of a table scan (for debugging).
    """
    result = SessionStoreTable(table).list_all()
    pp.pprint(result)


@cli.command(name="delete-user-tokens")
@table_argument
@user_option
def delete_user_tokens(table, user):
    """
    Deletes all session tokens for a user.
    """
    SessionStoreTable(table).delete_user_tokens(user)


if __name__ == '__main__':
    cli()
