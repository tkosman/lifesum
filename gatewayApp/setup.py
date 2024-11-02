import os

from setuptools import setup

def _get_requirements():
    path = f'{os.path.dirname(__file__)}/requirements.txt'
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().split()

setup(
    name='Gateway',
    version='1.0.0',
    packages=['gateway'],
    install_requires=_get_requirements(),
)
