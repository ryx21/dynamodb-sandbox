# Chapter 18: Building a Session Store

For this exercise, I've implemented the table design for a sessions store from Chapter 18. 

The table can be setup by running:

```commandline
python cli.py create-table <table>
```

This sets up a table with a simple primary key, with the `partition_column = SessionToken`. It also creates a GSI which is indexed by `Username`

The following access patterns are supported through a lightweight CLI in `cli.py`, which a simple wrapper of the boundary code `database.py` that makes requests to DynamoDB.:

```commandline
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add-token           Creates a session token for a user with a ttl.
  create-table        Creates a DynamoDB table.
  delete-table        Deletes a DynamoDB table.
  delete-user-tokens  Deletes all session tokens for a user.
  describe-table      Prints a description of the table.
  get-token           Prints the result of querying a table by the token id.
  list-all            Prints the result of a table scan (for debugging).
```

You can also run `python cli <command> --help` with a specific command to get information about the arguments and options for each one.