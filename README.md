## How to run our environment using docker? (be fancy)

### Run Node service
```bash
docker build -t docker-node -f docker/Dockerfile.node .
sudo docker run --network host --env-file ./nodeApp/.env docker-node
```

### Run Gateway service
```bash
docker build -t docker-gateway -f docker/Dockerfile.gateway .
docker run --network host docker-gateway
```
> NOTE: Do not use `-bg` option in docker as it will orphan our container :/

## To run Gateway the normal way
#### Create python venv using python 3.12 and activate it
```bash
python3.12 -m venv myenv
source ./myenv/bin/activate
```
#### Install all required packages:
```bash
pip install -r "requirements.txt"
```

#### Run the Gateway
```
python -m gateway
```
