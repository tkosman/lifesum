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

#### To use dev dockerfiles:
```
docker build -t docker-dev-node -f Dockerfile.dev.node . (run inside docker dir)
docker run -it -v ./nodeApp:/nodeApp -v ./Message:/Message --env-file ./nodeApp/.env docker-dev-node (run outside docker dir)
```
```
docker build -t docker-dev-gateway -f Dockerfile.dev.gateway . (inside docker dir)
docker run -it -v ./gatewayApp:/gatewayApp -v ./Message:/Message --network host docker-dev-gateway (run outside docker dir)
```