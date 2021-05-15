import datetime
import requests
import uuid

# TODO generalize for other non-cancer use cases
# http://build.fhir.org/ig/HL7/fhir-medmorph/Communication-communication-example-cancer-pha-response.html
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

# http://build.fhir.org/ig/HL7/fhir-medmorph/MessageHeader-messageheader-example-reportheader.html
message_header_stub = {
    "resourceType": "MessageHeader",
    "id": "messageheader-example-reportheader",
    "meta": {
        "versionId": "1",
        "lastUpdated": "2020-11-29T02:03:28.045+00:00",
        "profile": ["http://hl7.org/fhir/us/medmorph/StructureDefinition/us-ph-messageheader"]
    },
    "extension": [
        {
            "url": "http://hl7.org/fhir/us/medmorph/StructureDefinition/ext-dataEncrypted",
            "valueBoolean": False
        },
        {
            "url": "http://hl7.org/fhir/us/medmorph/StructureDefinition/ext-messageProcessingCategory",
            "valueCode": "consequence"
        }
    ],
    "eventCoding": {
        "system": "http://hl7.org/fhir/us/medmorph/CodeSystem/us-ph-messageheader-message-types",
        "code": "cancer-report-message"
    },
    "destination": [{
        "name": "PHA endpoint",
        "endpoint": "http://example.pha.org/fhir"
    }],
    "source": {
        "name": "Healthcare Organization",
        "software": "Backend Service App",
        "version": "3.1.45.AABB",
        "contact": {
            "system": "phone",
            "value": "+1 (917) 123 4567"
        },
        "endpoint": "http://example.healthcare.org/fhir"
    },
    "reason": {
        "coding": [{
            "system": "http://hl7.org/fhir/us/medmorph/CodeSystem/us-ph-triggerdefinition-namedevents",
            "code": "encounter-close"
        }]
    }
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
        # HAPI does not honor this ID and assigns a sequential ID; may be config issue
        "id": str(uuid.uuid4()),
        "subject": {"reference": f"Patient/{patient_id}"},
        "meta": {"lastUpdated": datetime.datetime.now().isoformat() + "Z"},
    })

    comm_response = requests.post(f"{fhir_url}/Communication", json=comm)
    comm_response.raise_for_status()
    return comm_response.json()


def process_message_operation(reporting_bundle, fhir_url):
    # TODO persist entire incoming reporting bundle?
    message_header = get_first_resource(
        resource_type="MessageHeader",
        bundle=reporting_bundle,
    ) or message_header_stub.copy()
    content_bundle = get_first_resource(resource_type="Bundle", bundle=reporting_bundle)
    patient = get_first_resource(resource_type="Patient", bundle=content_bundle)
    # TODO investigate whether to persist patient

    communication = create_communication(patient["id"], fhir_url)
    message_header["focus"] = [{"reference": f"Communication/{communication['id']}"}]
    message_header["id"] = str(uuid.uuid4())

    # http://build.fhir.org/ig/HL7/fhir-medmorph/Bundle-response-bundle-example.html
    response_bundle = {
        "resourceType": "Bundle",
        "type" : "message",
        "id": str(uuid.uuid4()),
        "entry":[
            {"resource": message_header},
            {"resource": communication},
        ],
    }
    return response_bundle