from setuptools import setup

setup(
    name='aardvark-api',
    install_requires=[
        'injector',
        'rpy2',
        'waitress'
    ],
    entry_points={
        'console_scripts': [
            'aardvark-api=aardvark_api:main'
        ],
    })
