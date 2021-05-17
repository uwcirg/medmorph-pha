import os
import json
import sys
from pytest import fixture


def json_from_file(request, filename):
    data_dir, _ = os.path.splitext(request.module.__file__)
    data_dir = f"{data_dir}_data"
    with open(os.path.join(data_dir, filename), 'r') as json_file:
        data = json.load(json_file)
    return data


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
    def raise_for_status(self):
        return True
    def json(self):
        return self._json


def mock_request(url, json):
    """Mock requests.post"""
    return MockedResponse(json)


# load fake requests module for mocking
fake_requests = type(sys)('requests')
fake_requests.post = mock_request
fake_requests.put = mock_request
sys.modules['requests'] = fake_requests
