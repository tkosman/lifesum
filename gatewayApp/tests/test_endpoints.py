"""
This file contains the tests for the endpoints in the app.
"""
from sanic_testing.testing import SanicTestClient

def test_hello(test_app):
    """ Test the hello endpoint. """
    test_client = SanicTestClient(test_app)
    _, response = test_client.get('/')
    assert response.status == 200
