import os
import json
from pytest import fixture

from medmorph_pha.app import create_app

@fixture
def app():
    return create_app(testing=True)


def json_from_file(request, filename):
    data_dir, _ = os.path.splitext(request.module.__file__)
    data_dir = f"{data_dir}_data"
    with open(os.path.join(data_dir, filename), 'r') as json_file:
        data = json.load(json_file)
    return data


@fixture
def org_example(request):
    return json_from_file(request, "Organization-example.json")


@fixture
def reporting_bundle_example(request):
    return json_from_file(request, "Bundle-reporting-bundle-example.json")


@fixture
def reporting_bundle_response_example(request):
    return json_from_file(request, "Bundle-response-bundle-example.json")


class MockedResponse():
    """Mock version of requests.response"""
    def __init__(self, json):
        self._json = json

    @property
    def status_code(self):
        return 200

    def raise_for_status(self):
        return True

    def json(self):
        return self._json
