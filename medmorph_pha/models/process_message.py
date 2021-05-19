import datetime
from flask import current_app, has_app_context
import requests
import uuid

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
    if not bundle:
        return

    for entry in bundle.get("entry", []):
        if entry.get("resource", {}).get("resourceType") == resource_type:
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
    if has_app_context():
        current_app.logger.debug("Fire request: %s %s %s", method, url, str(kwargs))
    return verb(url, **kwargs)


def upsert_fhir_resource(fhir_resource, fhir_url):
    """
    Create or update given resource, by logical ID

    See https://www.hl7.org/fhir/http.html#upsert
    """
    if not fhir_resource:
        raise ValueError("Can't upsert null resource")

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


def tag_with_identifier(fhir_resource, value):
    """Add a business identifier to given FHIR resource"""
    fhir_resource.setdefault("identifier", [])
    fhir_resource["identifier"].append({
        "use": "usual",
        "system": "https://cirg.washington.edu/process-message",
        "value": value,
    })
    return fhir_resource


def process_message_operation(reporting_bundle, fhir_url):
    # add a logical id, if not already set
    reporting_bundle.setdefault("id", str(uuid.uuid4()))
    bundle_id = reporting_bundle["id"]
    upsert_fhir_resource(fhir_resource=reporting_bundle, fhir_url=fhir_url)
    message_header = get_first_resource(
        resource_type="MessageHeader",
        bundle=reporting_bundle,
    ) or message_header_stub.copy()

    message_header["id"] = str(uuid.uuid4())
    communication = None
    content_bundle = get_first_resource(resource_type="Bundle", bundle=reporting_bundle)
    patient = get_first_resource(resource_type="Patient", bundle=content_bundle)
    if patient:
        patient = tag_with_identifier(patient, bundle_id)
        upsert_fhir_resource(fhir_resource=patient, fhir_url=fhir_url)

        communication = comm_stub.copy()
        communication.update({
            "id": str(uuid.uuid4()),
            "subject": {"reference": f"Patient/{patient['id']}"},
            "meta": {"lastUpdated": datetime.datetime.now().isoformat() + "Z"},
        })
        communication = tag_with_identifier(communication, bundle_id)
        communication = upsert_fhir_resource(fhir_resource=communication, fhir_url=fhir_url)
        message_header["focus"] = [{"reference": f"Communication/{communication['id']}"}]

    upsert_fhir_resource(fhir_resource=message_header, fhir_url=fhir_url)

    # http://build.fhir.org/ig/HL7/fhir-medmorph/Bundle-response-bundle-example.html
    response_bundle = {
        "resourceType": "Bundle",
        "type": "message",
        "id": str(uuid.uuid4()),
        "entry": [{"resource": message_header}],
    }
    if communication:
        response_bundle['entry'].append({"resource": communication})

    if has_app_context():
        current_app.logger.debug(
            "$process_message returning: %s", str(response_bundle))
    return response_bundle
