# The DynamoDB Book (Alex DeBrie)

## Summary

A repo for me to learn DynamoDB, mostly implementing the data modelling examples from *The DynamoDB Book, Alex DeBrie*.

## Setup

Install the AWS CLI tool following the official instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

To spin up a local instance of DynamoDB, ensure you have a recent version of `docker` installed and from the project root directory, run the following:

```commandline
docker compose up --detach
```

When finished, tear down the docker container using:
```commandline
docker compose down
```

You can verify the service is running `docker ps`, and you should see something like:

```commandline
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS          PORTS                    NAMES
71c93dfb98cb   amazon/dynamodb-local:latest   "java -jar DynamoDBL…"   22 minutes ago   Up 20 minutes   0.0.0.0:8000->8000/tcp   dynamodb-local
```

Check that you can interact with the local DynamoDB instance by running a simple CLI command ([reference](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.CLI.html#Tools.CLI.UsingWithDDBLocal)).

```commandline
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

The `--endpoint-url` flag tells the AWS CLI that you want to send requests to the local DynamoDB service we span up with `docker compose`. If you haven't created any tables yet, this should print out an empty list:

```json
{
    "TableNames": []
}
```

## Resources

**NoSQL Workbench**: a very useful tool for visualising and debugging tables:
* https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html

Links to docs for Python libraries used:
* https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
* https://github.com/svix/python-ksuid
* https://click.palletsprojects.com/en/8.1.x/