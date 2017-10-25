from setuptools import setup

setup(
    name='tubelocal',
    version='0.1.0',
    author='Shmuel Lamm | @snlamm',
    packages=['tubelocal'],
    description='JSON backend api to download, organize, and view youtube videos offline.',
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask_migrate',
        'pafy'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Video'
    ]
)
