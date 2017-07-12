from setuptools import setup, find_packages


def install_requires():
    with open('requirements') as reqs:
        install_req = [
            line for line in reqs.read().split('\n')
        ]
    return install_req


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="panchanga",
    url="https://github.com/dhoomakethu/panchanga",
    version="0.1",
    description="Panchanga CLI",
    long_description=readme(),
    keywords="Panchanga CLI",
    author="dhoomakethu",
    packages=find_packages(),
    install_requires=install_requires(),
    entry_points={
        'console_scripts': [
            'panchanga = panchanga.cli.main:run_cli',
        ],
    },
    dependency_links=["https://github.com/dhoomakethu/pyphoon/tarball/master#egg=pyphoon-1.0"],
    include_package_data=True
)