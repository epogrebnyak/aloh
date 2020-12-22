from setuptools import setup

VERSION = "0.2.0"

setup(
    name="aloh",
    version=VERSION,
    description="Production planning with PuLP",
    author="Evgeniy Pogrebnyak",
    author_email="e.pogrebnyak@gmail.com",
    package_dir={'': 'src'},
    packages=['aloh'],
    install_requires=["numpy==1.19.3", "pandas==1.1.4", "PuLP==2.3.1"],
    python_requires=">=3.6",
)
