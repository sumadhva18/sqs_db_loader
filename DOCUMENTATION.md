# SQS to Postgres Loader

This repository contains a Python library that reads, validates, and loads data from SQS into a Postgres database.

## Installation Requirements

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

## Verification

Verify whether Docker is installed properly by executing the following commands:

```bash
$ docker --version
Docker version 29.3.1, build 1.fc43

$ docker-compose --version
Docker Compose version 5.1.1
```

## Prerequisites

* Download the [docker-compose.yml](https://github.com/sumadhva18/sqs_db_loader/blob/main/docker-compose.yml) file from GitHub to execute the Python script that loads data from SQS into Postgres.

* Set the LocalStack auth token. If you don’t have one, create a LocalStack account and navigate to `Settings > Auth Tokens` to generate a new token.

  * Use the following command to set the environment variable:

    ```bash
    $ export LOCALSTACK_AUTH_TOKEN=<AUTH_TOKEN>
    ```

  * Or set it in `~/.bashrc` so it persists across sessions:

    ```bash
    $ cat >> ~/.bashrc
    export LOCALSTACK_AUTH_TOKEN=<AUTH_TOKEN>
    CTRL-Z

    $ source ~/.bashrc
    ```

## Execution

Navigate to the directory where the [docker-compose.yml](https://github.com/sumadhva18/sqs_db_loader/blob/main/docker-compose.yml) file is located and run the following command:

This command starts the following containers:

* `localstack`
* `postgres`
* `app`

```bash
$ docker compose up
```

Run the following command to verify the data loaded into the Postgres table:

```bash
$ docker exec -it postgres psql -U postgres -d app_db -c "SELECT * FROM app_db.sqs.trip_details;"
```

## Logs

Use the following commands to check logs from each container:

* To check application logs:

  ```bash
  $ docker logs app
  ```

* To check Postgres logs:

  ```bash
  $ docker logs postgres
  ```

* To check LocalStack (SQS) logs:

  ```bash
  $ docker logs localstack
  ```

## Terminate

Stop all containers and remove associated volumes using the following command:

```bash
$ docker compose down -v
```

## Challenges

### Local Development

1. Setting up LocalStack with an auth token for local development.
2. Setting up the Postgres database and ensuring that the Python script can connect to it.

### Docker

1. After development, replicating the setup in Docker and ensuring that all three components (LocalStack, Postgres, app) work as expected.
2. Facing challenges connecting the application to LocalStack and Postgres within Docker. This was resolved by understanding how containers communicate using container names, URLs, and ports.
3. Initial testing was done by mounting local development code into Docker. Later, the code was moved to GitHub, and the Docker configuration was updated accordingly.

## Understanding

The JSON read and parsed from the SQS queue is transformed into the following format:

```json
{
    "id": 1,
    "mail": "aaa@gmail.com",
    "name": "AAA SSS",
    "trip": [
        {
            "departure": "A",
            "destination": "D",
            "start_date": "2022-10-10 12:15:00",
            "end_date": "2022-10-10 13:55:00"
        }
    ]
}
```

There are two different types of inputs:

* The following JSON input has two `from` and `to` entries, so it will be loaded as two separate rows:

```json
{
	"id": 3,
	"mail": "aaa@gmail.com",
	"name": "Mahmoud",
	"surname": "Mahmoudi",
	"route": [
		{
			"from": "B",
			"to": "C",
			"duration": 15,
			"started_at": "10/10/2022 11:10:00"
		},
		{
			"from": "C",
			"to": "E",
			"duration": 10,
			"started_at": "10/10/2022 11:17:15"
		}
	]
}
```

* The following JSON input contains two locations. The one with the minimum timestamp is considered the departure location, and the other is considered the destination.

In this case, the departure location will be `F` and the destination will be `G`:

```json
{
	"id": 5,
	"mail": "mmm@nocompany.com",
	"name": "Kacper",
	"surname": "Kacperian",
	"locations": [
		{
			"location": "F",
			"timestamp": 1667999699
		},
		{
			"location": "G",
			"timestamp": 1668975653
		}
	]
}
```

* The combination of the following columns provides unique records in the table:

  * `id`
  * `departure`
  * `destination`
  * `start_timestamp`