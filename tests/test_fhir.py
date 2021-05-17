from medmorph_pha.models.process_message import process_message_operation


def test_process_message(reporting_bundle_example, reporting_bundle_response_example):
    response_bundle = process_message_operation(
        reporting_bundle=reporting_bundle_example,
        fhir_url="http://fake.com/fhir",
    )

    assert response_bundle["resourceType"] == "Bundle"
    assert len(response_bundle["type"]) == len(reporting_bundle_response_example["type"])
    assert len(response_bundle["entry"]) == len(reporting_bundle_response_example["entry"])
