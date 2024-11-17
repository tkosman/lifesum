from setuptools import setup, find_packages

setup(
    name='nodeApp',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'eth-brownie==1.20.0',
        'pytest==6.2.5',
        'pytest-xdist==2.2.1',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
