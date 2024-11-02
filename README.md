## To run Gateway
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
