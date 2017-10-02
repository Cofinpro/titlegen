from setuptools import setup

setup(
        name='titlegen',
        packages=['titlegen'],
        include_package_data=True,
        install_requires=[
            'gunicorn',
            'flask',
            'flask_wtf',
        ],
)
