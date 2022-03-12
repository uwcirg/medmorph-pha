from flask import Blueprint, abort, current_app, jsonify, request

from medmorph_pha.models.process_message import (
    process_message_operation,
    remote_request,
)

blueprint = Blueprint('fhir', __name__, url_prefix='/fhir')
ALL_METHODS=['DELETE', 'GET', 'OPTIONS', 'POST', 'PUT']


@blueprint.route('/$process-message', methods=['POST'])
def process_message():
    fhir_json = request.json
    if not fhir_json:
        abort(400, "POST requires valid FHIR Bundle as Content-Type: application/json")
    response = process_message_operation(fhir_json, fhir_url=current_app.config["BACKING_FHIR_URL"])
    return response


@blueprint.route('/', defaults={'relative_path': ''}, methods=ALL_METHODS)
@blueprint.route('/<path:relative_path>', methods=ALL_METHODS)
def route_fhir(relative_path):
    backing_fhir_base_url = current_app.config['BACKING_FHIR_URL']
    backing_fhir_url = '/'.join((backing_fhir_base_url, relative_path))
    backing_headers = {}
    if 'Authorization' in request.headers:
        backing_headers = {'Authorization': request.headers['Authorization']}

    backing_response = remote_request(
        method=request.method,
        url=backing_fhir_url,
        headers=backing_headers,
        params=request.args,
    )
    response = jsonify(backing_response.json())
    response.status_code = backing_response.status_code
    return response


@blueprint.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = ", ".join(('Authorization','Content-Type'))

    return response


@blueprint.before_app_request
def debug_request_dump():
    if current_app.config.get("DEBUG_DUMP_HEADERS"):
        current_app.logger.debug("{0.remote_addr} {0.method} {0.path} {0.headers}".format(request))
    if current_app.config.get("DEBUG_DUMP_REQUEST"):
        output = "{0.remote_addr} {0.method} {0.path}"
        if request.data:
            output += " {data}"
        if request.args:
            output += " {0.args}"
        if request.form:
            output += " {0.form}"
        current_app.logger.debug(output.format(
            request,
            data=request.get_data(as_text=True),
        ))
