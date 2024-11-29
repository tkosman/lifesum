#! /bin/bash
docker build -f Dockerfile.pytest -t gateway-pytest .
docker run gateway-pytest
