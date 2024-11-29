## To run and test Gateway using docker (being fancy)
### Run application
```bash
docker build -t docker-gateway .
docker run -p 1234:1234 docker-gateway
```
> NOTE: Do not use `-bg` option in docker as it will orphan our container :/

### Run pytest:
```bash
./run-pytest.sh
```

## To run Gateway the usual way
### Create python venv using python 3.12 and activate it
```bash
python3.12 -m venv myenv
source ./myenv/bin/activate
```
### Install all required packages:
```bash
pip install -r "requirements.txt"
```

### Run the Gateway
```
python -m gateway
```

## To test
```bash
pip install -r "requirements-test.txt"
pytest
```
