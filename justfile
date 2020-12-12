main := "src/aloh"
deps := "_requirements.txt"
env := "env1"

# ensure codepage
codepage:
  set PYTHONIOENCODING=utf8  
  chcp 1251

# install dependencies
pip-install:
  pip install -r {{deps}}

# start environment
env-start:
  @echo call {{env}}\Scripts\activate.bat

# install package locally
setup-dev:
  pip install -e .

# black and isort
lint:
  black {{main}}
  isort {{main}}

# start docs server
serve:
  mkdocs serve

# start Jupyter lab in examples
lab:
  jupyter notebook --notebook-dir="examples"

# run all examples
examples-all:
  python examples/example0.py
  python examples/example1a.py
  python examples/example2.py