from setuptools import setup

version = ".".join(open('writepromd/__init__.py').read().split('__version__ = ')[1].split('.')[0:3]).strip("'").strip('"')

setup(
    name='WriteProMD',
    version=version,
    description='Converts markdown-like syntax documents to polished PDFs with a wide range of formatting options',
    author='Almog Cohen',
    author_email='me@almogcohen.com',
    url='https://github.com/almog-co/WriteProMD',
    packages=['writepromd'],
    entry_points={
        'console_scripts': ['writepromd = writepromd.writepromd:main']
    },
    install_requires=[
        'fpdf~=1.0'
    ]
)