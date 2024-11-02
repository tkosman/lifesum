"""
This file contains fixtures that are used in the tests.
"""

import argparse
import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # to import main module
print(os.path.join(os.path.dirname(__file__), '..'))
from gateway.__main__ import create_app

@pytest.fixture(scope='session')
def args():
    """Mock arguments for the app."""
    arguments = argparse.Namespace()
    arguments.ip = '127.0.0.1'
    arguments.port = 1111

    return arguments


@pytest.fixture(scope='session')
def test_app(args):
    return create_app(args)
