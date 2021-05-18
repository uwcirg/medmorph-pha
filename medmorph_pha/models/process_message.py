import datetime
from flask import current_app, has_app_context
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


def remote_request(method, url, **kwargs):
    verbs = {
        "delete": requests.delete,
        "get": requests.get,
        "options": requests.options,
        "post": requests.post,
        "put": requests.put,
    }
    verb = verbs[method.lower()]
    current_app.logger.debug("Fire request: %s %s %s", method, url, str(kwargs))
    return verb(url, **kwargs)


def upsert_fhir_resource(fhir_resource, fhir_url):
    """
    Create or update given resource, by logical ID

    See https://www.hl7.org/fhir/http.html#upsert
    """

    logical_id = fhir_resource.get("id", "")
    resource_type = fhir_resource["resourceType"]
    if has_app_context():
        current_app.logger.debug("Upsert %s(id=%s)", resource_type, logical_id)

    request_method = 'put' if logical_id else 'post'
    response = remote_request(
        method=request_method,
        url=f"{fhir_url}/{resource_type}/{logical_id}",
        json=fhir_resource)
    response.raise_for_status()
    return response.json()


def create_communication(patient_id, fhir_url):
    """Create Communication resource from given patientId and persist"""
    comm = comm_stub.copy()
    comm.update({
        "id": str(uuid.uuid4()),
        "subject": {"reference": f"Patient/{patient_id}"},
        "meta": {"lastUpdated": datetime.datetime.now().isoformat() + "Z"},
    })

    new_comm = upsert_fhir_resource(fhir_resource=comm, fhir_url=fhir_url)
    return new_comm


def process_message_operation(reporting_bundle, fhir_url):
    upsert_fhir_resource(fhir_resource=reporting_bundle, fhir_url=fhir_url)
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
    upsert_fhir_resource(fhir_resource=message_header, fhir_url=fhir_url)

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
    if has_app_context():
        current_app.logger.debug(
            "$process_message returning: %s", str(response_bundle))
    return response_bundle
