from setuptools import setup

setup(
    name='tongbu_cli',
    version='0.1',
    py_modules=['tongbu_cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        tongbu_cli=tongbu_cli:cli
    ''',
)
