# Chapter 18: Building a Session Store

For this exercise, I've implemented the table design for a sessions store from Chapter 18. 

The table can be setup by running:

```commandline
python cli.py create <table>
```

This sets up a table with a simple primary key, with the `partition_column = SessionToken`. It also creates a GSI which is indexed by `Username`

Then the following access patterns are supported through a lightweight CLI in `cli.py`, which a simple wrapper of the boundary code `database.py` that makes requests to DynamoDB.:

```commandline
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add-token             # adding a new session token
  create                # creats a table
  delete                # deletes a table
  delete-token          # deleting a known token
  delete-user-tokens    # deleting all tokens associated with a user
  describe              # runs the describe table command
  get-token             # retrieving an item using the session token
  list-all              # lists all items (for debugging)
```

You can also run `python cli <command> --help` with a specific command to get information about the arguments and options for each one.