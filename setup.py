import pathlib
from io import open

from setuptools import find_packages, setup


def parse_requirements(filename):
    with open(filename) as file:
        lines = file.read().splitlines()

    return [
        line.strip()
        for line in lines
        if not (
            (not line) or
            (line.strip()[0] == "#") or
            (line.strip().startswith('--find-links')) or
            ("git+https" in line)
        )
    ]


def get_dependency_links(filename):
    with open(filename) as file:
        lines = file.read().splitlines()

    return [
        line.strip().split('=')[1]
        for line in lines
        if line.strip().startswith('--find-links')
    ]


dependency_links = get_dependency_links('requirements.txt')
parsed_requirements = parse_requirements('requirements.txt')

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name="pypi-stats-graphs",
    version="1.0",
    author="Lalit Pagaria",
    author_email="pagaria.lalit@gmail.com",
    description="To generate various graphs from PYPI download stats",
    long_description=README,
    long_description_content_type="text/markdown",
    license="Apache Version 2.0",
    url="https://github.com/lalitpagaria/pypi-stats-graphs",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    dependency_links=dependency_links,
    install_requires=parsed_requirements,
    include_package_data=True,
    python_requires=">=3.6.0",
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
