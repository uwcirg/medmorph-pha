Public Health Authority role for MedMorph IG
============================================
A simple flask proxy wrapped around HAPI FHIR, providing $process-message operation

Development
-----------
To start the application follow the below steps in the checkout root

Copy default environment variable file and modify as necessary

    cp medmorph_pha.env.default medmorph_pha.env

Build the docker image. Should only be necessary on first run or if dependencies change.

    docker-compose build

Start the container in detached mode

    docker-compose up --detach

Read application logs

    docker-compose logs --follow


Test
----
Invoke the test runner from the root directory as follows:

    tox

License
-------
BSD
