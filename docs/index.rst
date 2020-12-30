aloh
====

.. toctree::
   :maxdepth: 2
   :hidden:

   overview
   formulas/english
   api

Idea
----

We have some documentation generated from markdown files by mkdocs already (in Russian),
but not from docstrings (should be in English). We will end up with a documentation 
site in English (build with Sphinx) and a promo site in Russian built in mkdocs based
on independent markdown source files.

Current directories and files:

 - shpynx: conf.py, documentation / site2 
 - mkdocs: mkdocs.yml, docs / site

There are also some commands in "just" file associated with documentation 
but they are work in progress. Just is a kind of make-like tool.
<https://github.com/casey/just>

We do not publish Sx docs anywhere yet, the mkdocs go to github pages.

Todo
----

1. Markdown/sources:

- 1.1 allow markdown source files (via [MyST](https://myst-parser.readthedocs.io/en/latest/) maybe?)
- 1.2 show the rendering of formulas from markdown is possible: $\sum X_{ij}$

2. Presentation/layout:

- what controls chapter contents in left vertical side bar of pydata theme?  

3. Docstring parsing:

- how to exclude some public methods docstrings from generated API documentation?


Not todo
--------

- we shall need some transport to publish to Github Pages (ghp-import maybe)
- maybe Russian mkdocs and English pydata/Sx docs can coexist in one site 
- publish to separate S3 bucket 

Excercises
----------

1. build stand-alone .rst file with Sx
2. build a collection of .rst files with Sx
3. change theme of the documentation
4. document your API - module example
5. document your API - package example
6. neat things rst provides you (eg glossary)
7. publish you documentation 
8. automate repeated tasks
9. why Sx is hard to grasp and run and what to do about it
10. Sx alternatives ()

How to run 
-----------

Build this site from repo root folder:

  sphinx-build -a -c . documentation site2

Point your browser to site2/index.html.


Links
-----

- https://pydata-sphinx-theme.readthedocs.io/en/latest/
- https://www.sphinx-doc.org/en/master/
- https://raw.githubusercontent.com/Pylons/pyramid/1.10-branch/docs/index.rst
- https://docs.pylonsproject.org/projects/pyramid/en/latest/index.html
