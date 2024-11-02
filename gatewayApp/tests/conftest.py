"""
This file contains fixtures that are used in the tests.
"""

import argparse
import os
import sys

import pytest
from sanic_testing.testing import SanicTestClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # to import main module
from gateway.__main__ import create_app
from utils.key_generator import generate_test_key_pair
from utils.challenge_decoder import sign_challenge

@pytest.fixture(scope='session')
def args():
    """Mock arguments for the app."""
    arguments = argparse.Namespace()
    arguments.ip = '127.0.0.1'
    arguments.port = 1111

    return arguments

@pytest.fixture(scope='session')
def test_app(args):
    """ Create a test app for the tests."""
    return create_app(args)

@pytest.fixture(scope='session')

def test_client(test_app):
    """ Create sanic test client."""
    return SanicTestClient(test_app)

@pytest.fixture(scope="module")
def key_pair():
    """ Generate a key pair for testing."""
    return generate_test_key_pair()

@pytest.fixture(scope="module")
def public_key(key_pair):
    """ Get the public key from the key pair."""
    return key_pair[1]

@pytest.fixture(scope="module")
def private_key(key_pair):
    """ Get the private key from the key pair."""
    return key_pair[0]

@pytest.fixture(scope="module")
def sign_challenge_func_fixture():
    """ Return the sign_challenge function for testing."""
    return sign_challenge
