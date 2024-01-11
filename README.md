# eCR Connectathon
Hapi FHIR, and a simple flask proxy wrapped around HAPI FHIR, providing `$process-message` operation

## Development

To start the application follow the below steps in the checkout root

Copy default environment files and modify as necessary

    cp fhir-proxy.env.default fhir-proxy.env
    cp default.env .env

Build the docker image. Should only be necessary on first run or if dependencies change.

    docker-compose build

Start the container in detached mode

    docker-compose up --detach

Read application logs

    docker-compose logs --follow


## Test
Invoke the test runner from the root directory as follows:

    tox
