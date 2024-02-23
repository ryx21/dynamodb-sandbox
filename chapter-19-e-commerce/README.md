# Chapter 19: Building an E-Commerce Application

For this exercise, I've implemented the table design for an e-commerce order management system from Chapter 19.

This supports a number of access patterns, exposed through a lightweight CLI for illustration:

```commandline
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add-address          Adds or replaces an address to a customer.
  create-customer      Creates a new customer entity.
  create-order         Creates a customer order.
  create-table         Creates a table.
  customer-orders      Gets items for a customer and the last N orders.
  delete-address       Deletes an address for a customer.
  delete-table         Deletes a table.
  describe-table       Prints a description of the table.
  list-all             Prints the result of a table scan (debugging).
  order-items          Gets items for an order and N order items.
  update-order-status  Updates an order status.
```
