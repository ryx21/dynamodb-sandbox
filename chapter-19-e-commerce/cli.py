import click
import pprint
import json
from typing import List
from database import ECommerceTable

pp = pprint.PrettyPrinter(indent=2)

table_argument = click.argument("table")
username_option = click.option("--username", required=True, type=str)
order_id_option = click.option("--order-id", required=True, type=str)


@click.group()
def cli():
    pass


@cli.command(name="create-table")
@click.argument("table")
def create_table(table: str):
    """
    Creates a table.
    """
    ECommerceTable(table).create_table()


@cli.command(name="delete-table")
@table_argument
def delete_table(table: str):
    """
    Deletes a table.
    """
    ECommerceTable(table).delete_table()


@cli.command(name="describe-table")
@table_argument
def describe_table(table: str):
    """
    Prints a description of the table.
    """
    result = ECommerceTable(table).describe_table()
    pp.pprint(result)


@cli.command(name="list-all")
@table_argument
def list_all(table):
    """
    Prints the result of a table scan (debugging).
    """
    result = ECommerceTable(table).list_all()
    pp.pprint(result)


@cli.command(name="create-customer")
@table_argument
@username_option
@click.option("--email", required=True, type=str)
@click.option("--name", required=True, type=str)
def create_customer(table, username: str, email: str, name: str):
    """
    Creates a new customer entity.
    """
    ECommerceTable(table).create_customer(
        username=username,
        email_address=email,
        name=name
    )


@cli.command(name="add-address")
@table_argument
@username_option
@click.option("--address-name", required=True, type=str)
@click.option("--address-details", required=True, type=str)
def add_address(table: str, username: str, address_name: str, address_details: str):
    """
    Adds or replaces an address to a customer.
    """
    ECommerceTable(table).add_customer_address(
        username=username,
        address_name=address_name,
        address_details=address_details
    )


@cli.command(name="delete-address")
@table_argument
@username_option
@click.option("--address-name", required=True, type=str)
def delete_address(table: str, username: str, address_name: str):
    """
    Deletes an address for a customer.
    """
    ECommerceTable(table).delete_customer_address(
        username=username,
        address_name=address_name
    )


@cli.command(name="create-order")
@table_argument
@username_option
@click.option("--item", required=True, type=str, multiple=True)
def create_order(table: str, username: str, item: List[str]):
    """
    Creates a customer order.

    Provide 1 or more '--item' options as a JSON string, which must have attributes
    - "price" (number)
    - "description" (string)
    """
    # create list of dict of items which should each have attributes "price" (number) and description (string)
    item_dicts = [json.loads(i) for i in item]
    ECommerceTable(table).create_order(
        username=username,
        order_items=item_dicts
    )


@cli.command(name="update-order-status")
@table_argument
@username_option
@order_id_option
@click.option("--status", required=True, type=click.Choice(["ACCEPTED", "SHIPPED", "DELIVERED", "CANCELLED"]))
def update_order_status(table: str, username: str, order_id: str, status: str):
    """
    Updates an order status.

    Must be one of ["ACCEPTED", "SHIPPED", "DELIVERED", "CANCELLED"]
    """
    ECommerceTable(table).update_order_status(
        username=username,
        order_id=order_id,
        status=status
    )


@cli.command(name="customer-orders")
@table_argument
@username_option
@click.option("--limit", required=False, default=10, type=int)
def get_customer_orders(table: str, username: str, limit: int):
    """
    Gets items for a customer and the last N orders.
    """
    result = ECommerceTable(table).get_customer_and_orders(
        username=username,
        limit=limit
    )
    pp.pprint(result)


@cli.command(name="order-items")
@table_argument
@order_id_option
@click.option("--limit", required=False, default=10, type=int)
def order_items(table: str, order_id: str, limit: int):
    """
    Gets items for an order and N order items.
    """
    result = ECommerceTable(table).get_order_and_order_items(
        order_id=order_id,
        limit=limit
    )
    pp.pprint(result)


if __name__ == "__main__":
    cli()
