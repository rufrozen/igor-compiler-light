from setuptools import setup

setup(
    name='IgorCompiller',
    version='0.1.8',
    description='Script language for describing REST protocol. Include Typescript code generator for client and Document generator. ',
    author='Igor Timurov',
    author_email='rufrozen@yandex.ru',
    url='https://github.com/rufrozen/igor-compiler-light',
    install_requires = [
        'pypeg2',
        'inflection'
    ],
    packages=['igor_compiler']
)


