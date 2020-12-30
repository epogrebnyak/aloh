main := "src/aloh"
docs := "docs"
deps := "requirements.txt"
deps_dev := "requirements-dev.txt"
env := "env1"


# build sphinx documentation locally
sx-build:
  sphinx-build -a docs site

# create rst source for API documentation
sx-apidoc:
  sphinx-apidoc -f -o docs src test_*.*  

# build mkdocs documentation locally
mkdocs-build:
  mkdocs build

# start documentation server (mkdocs)
mkdocs-serve:
  mkdocs serve

# install dependencies
pip-r:
  pip install -r {{deps}}

# install dev dependencies
pip-dev:
  pip install -r {{deps_dev}}

# install package from git
install-git:
  pip install -U git+https://github.com/epogrebnyak/aloh.git  

# install package locally (editable)
install-dev:
  pip install -U -e .

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
docs-publish:  
  mkdocs gh-deploy

# project-specific
# ensure codepage
win-codepage:
  set PYTHONIOENCODING=utf8  
  chcp 1251

# run all examples
#examples-all:
#  python examples/example0.py
#  python examples/example1a.py
#  python examples/example2.py

