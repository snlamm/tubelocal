from setuptools import setup

setup(
    name='tubelocal',
    packages=['tubelocal'],
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy'
    ],
)
