import datetime
import requests
import uuid

# TODO generalize for other non-cancer use cases
# https://github.com/drajer-health/ecr-on-fhir/blob/master/fhir-eicr-r4/src/main/java/org/sitenv/spring/MessageHeaderResourceProvider.java#L150
comm_stub = {
    "resourceType": "Communication",
    "meta": {
        "versionId": "1",
        "profile": ["http://hl7.org/fhir/us/medmorph/StructureDefinition/us-ph-communication"]
    },
    "extension": [{
        "url": "http://hl7.org/fhir/us/medmorph/StructureDefinition/ext-responseMessageStatus",
        "valueCodeableConcept": {
            "coding": [{
                "system": "http://hl7.org/fhir/us/medmorph/CodeSystem/us-ph-response-message-processing-status",
                "code": "RRVS1"
            }]
        }
    }],
    "identifier": [{
        "system": "http://example.pha.org/",
        "value": "12345"
    }],
    "status": "completed",
    "category": [{
        "coding": [{
            "system": "http://hl7.org/fhir/us/medmorph/CodeSystem/us-ph-messageheader-message-types",
            "code": "cancer-response-message"
        }]
    }],
    "reasonCode": [{
        "coding": [{
            "system": "http://hl7.org/fhir/us/medmorph/CodeSystem/us-ph-messageheader-message-types",
            "code": "cancer-report-message"
        }]
    }]
}

response_bundle_stub = {
    "resourceType": "Bundle",
    "entry":[]
}


def get_first_resource(resource_type, bundle):
    """Iterate through the given bundle, returning the first matching resource of given type"""
    for entry in bundle["entry"]:
        if entry["resource"]["resourceType"] == resource_type:
            return entry["resource"]


def create_communication(patient_id, fhir_url):
    """Create Communication resource from given patientId and persist"""
    comm = comm_stub.copy()
    comm.update({
        "id": uuid.uuid4(),
        "subject": {"reference": f"Patient/{patient_id}"},
        "meta": {"lastUpdated": datetime.datetime.now().isoformat() + "Z"},
    })

    comm_response = requests.post(f"{fhir_url}/Communication", json=comm)
    comm_response.raise_for_status()
    return comm_response.json()


def process_message_operation(reporting_bundle, fhir_url):
    # TODO persist entire incoming reporting bundle?
    # TODO return stub MessageHeader if absent
    # https://github.com/drajer-health/ecr-on-fhir/blob/master/fhir-eicr-r4/src/main/java/org/sitenv/spring/MessageHeaderResourceProvider.java#L143
    message_header = get_first_resource(resource_type="MessageHeader", bundle=reporting_bundle)
    content_bundle = get_first_resource(resource_type="Bundle", bundle=reporting_bundle)
    patient = get_first_resource(resource_type="Patient", bundle=content_bundle)
    # TODO investigate whether to persist patient

    comm_id = create_communication(patient["id"], fhir_url)["id"]
    message_header["focus"] = [{"reference": f"Communication/{comm_id}"}]
    message_header["id"] = uuid.uuid4()

    response_bundle = response_bundle_stub.copy()
    response_bundle["id"] = uuid.uuid4()
    response_bundle["entry"].append({"resource": message_header})

    return response_bundle
