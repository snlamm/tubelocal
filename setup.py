from setuptools import setup

setup(
    name='tubelocal',
    author='Shmuel Lamm | @snlamm',
    packages=['tubelocal'],
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'pafy'
    ],
)
