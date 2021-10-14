import setuptools
import os

requirements = list()
requirements_file = 'requirements.txt'
if os.access(requirements_file, os.R_OK):
    with open(requirements_file, 'r') as requirements_file_pointer:
        requirements = requirements_file_pointer.read().split()
setuptools.setup(
    scripts=['ping_exporter/ping_exporter.py'],
    author="Antonio J. Delgado",
    version='0.0.1',
    name='ping_exporter',
    author_email="",
    url="",
    description="",
    license="GPLv3",
    install_requires=requirements,
    #keywords=["my", "script", "does", "things"]
)
