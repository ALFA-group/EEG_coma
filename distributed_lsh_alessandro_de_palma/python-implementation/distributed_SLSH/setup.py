from setuptools import setup, find_packages

requirements = [
    'numpy',
]

setup(
    name='distributed_SLSH',
    author='Alessandro De Palma',
    author_email='adepalma@mit.edu',
    description='',
    packages=['middleware', 'worker_node'],
    install_requires=requirements,
)