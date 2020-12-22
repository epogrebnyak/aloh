main := "src/aloh"
docs := "docs"
deps := "requirements.txt"
env := "env1"

# install dependencies
pip-install:
  pip install -r {{deps}}

install-git:
  pip install git+https://github.com/epogrebnyak/aloh.git  

# install package locally
install-dev:
  pip install -e .
# start environment
env-start:
  @echo call {{env}}\Scripts\activate.bat


# black and isort
lint:
  black {{main}}
  isort {{main}}

# start Jupyter lab in examples
lab:
  jupyter notebook --notebook-dir="examples"

# publish documentation to GitHub Pages
publish:
  ghp-import -p docs

# start docs server
serve:
  mkdocs serve

# project-specific
# ensure codepage
win-codepage:
  set PYTHONIOENCODING=utf8  
  chcp 1251

# run all examples
examples-all:
  python examples/example0.py
  python examples/example1a.py
  python examples/example2.py