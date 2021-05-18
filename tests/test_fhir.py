from flask import url_for

from conftest import MockedResponse
from medmorph_pha.models.process_message import process_message_operation


def test_process_message(
        mocker, reporting_bundle_example, reporting_bundle_response_example):
    # Patch remote_request to interrupt call to HAPI during process message
    mr = MockedResponse(reporting_bundle_response_example)
    mocker.patch(
        'medmorph_pha.models.process_message.remote_request',
        return_value=mr)

    response_bundle = process_message_operation(
        reporting_bundle=reporting_bundle_example,
        fhir_url="http://fake.com/fhir",
    )

    assert response_bundle["resourceType"] == "Bundle"
    assert len(response_bundle["type"]) == len(reporting_bundle_response_example["type"])
    assert len(response_bundle["entry"]) == len(reporting_bundle_response_example["entry"])


def test_passthrough_put(client, mocker, org_example):
    mr = MockedResponse(org_example)
    mocker.patch(
        'medmorph_pha.api.fhir.remote_request',
        return_value=mr)
    response = client.put(
        url_for('fhir.route_fhir', relative_path='Organization/hl7'),
        json=org_example)
    assert response.status_code == 200
    assert response.json['id'] == 'hl7'
    assert response.headers['Access-Control-Allow-Headers'] == 'Authorization'
