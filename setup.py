from setuptools import setup

setup(
    name="Flask-Upload",
    version="0.1dev",
    url="http://github.com/spectralsun/flask-upload",
    license="MIT",
    install_requires=[
        'Flask>=0.10.1',
        'Pillow>=2.2.1'
    ],
    packages=['flask_upload']
)