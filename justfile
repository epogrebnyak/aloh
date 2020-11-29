main := "aloh.py"

env-start:
  call env1\Scripts\activate.bat

# install package locally
setup-dev:
  pip install -e .

lint:
  black .