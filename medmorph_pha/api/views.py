from flask import Blueprint, render_template, url_for

base_blueprint = Blueprint('base', __name__)


@base_blueprint.route('/')
def root():
    return {'ok': True}


@base_blueprint.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


@base_blueprint.route('/reports')
def reports():
    """Build up table of received reports from queried FHIR data"""
    from .fhir import route_fhir

    def bundle_data():
        """Obtain bundles and metadata such as lastUpdated for each"""
        results = []
        all_bundles = route_fhir(relative_path='Bundle').json
        for bundle in all_bundles['entry']:
            # Don't know join syntax, loop over and request metadata
            id = bundle["resource"]["id"]
            relative_path = f'Bundle/{id}'
            bundle_resource = route_fhir(relative_path=relative_path).json
            results.append({
                'id': id,
                'url': url_for('fhir.route_fhir', relative_path=relative_path),
                'last_updated': bundle_resource['meta']['lastUpdated']})
        return results

    return render_template("reports.html", bundles=bundle_data())
