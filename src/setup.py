from setuptools import setup

setup(
    name='password_inator',
    version='0.1.0',
    py_modules=['main', 'getch', 'account', 'password_utils', 'prompter'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'password-inator = main:cli',
        ],
    },
)