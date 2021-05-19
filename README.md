Public Health Authority role for MedMorph IG
============================================
A simple flask proxy wrapped around HAPI FHIR, providing `$process-message` operation

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

To feed a sample file via ``curl``, start the container as mentioned above and call:

    curl \
      -H "Content-Type: application/json" \
      -X POST -d @tests/test_fhir_data/Bundle_us-ph-report.json \
      "http://localtest.me:5000/fhir/\$process-message"

License
-------
BSD
