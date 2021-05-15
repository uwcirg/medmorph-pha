import requests

from flask import Blueprint, abort, current_app, request, session, g

from medmorph_pha.models.process_message import process_message_operation

blueprint = Blueprint('fhir', __name__, url_prefix='/fhir')


@blueprint.route('/$process-message', methods=['POST'])
def process_message():
    fhir_json = request.json
    response = process_message_operation(fhir_json)
    return response


@blueprint.route('/', defaults={'relative_path': ''})
@blueprint.route('/<path:relative_path>')
def route_fhir(relative_path):
    backing_fhir_base_url = current_app.config['BACKING_FHIR_URL']
    backing_fhir_url = '/'.join((backing_fhir_base_url, relative_path))
    backing_headers = {}
    if 'Authorization' in request.headers:
        backing_headers = {'Authorization': request.headers['Authorization']}

    # TODO pass all HTTP verbs, not just GET
    backing_response = requests.get(
        url=backing_fhir_url,
        headers=backing_headers,
        params=request.args,
    )
    return backing_response.json(), backing_response.status_code


@blueprint.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization'

    return response
