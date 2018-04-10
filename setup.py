import io
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def load_requirements(filename):
    with io.open(filename, encoding='utf-8') as reqfile:
        return [line.strip() for line in reqfile if not line.startswith('#')]


setup(
    name='yuna',
    version='0.2.0',
    description='A quantitative analyse for Assets',
    long_description=long_description,
    url='https://github.com/Na0ture/yuna',
    author='Lv Zhi',
    author_email='279094354@qq.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=load_requirements('requirements.txt'),
    package_data={
        '': ['all.pkl'],
    },
    entry_points={
        'console_scripts': [
            'yuna=yuna_cli.cli:cli',
        ],
    },
)
