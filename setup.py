from setuptools import setup


install_requires = [
    'PyAutoGUI >= 0.9, < 1.0',
    'pywin32 >= 221, < 230',
    'pywinauto >= 0.6, < 0.7',
    'psutil >= 5.7.0, < 5.8.0',
    'typing-extensions >= 3.7, < 3.8',
]

setup(
    name='creon',
    version='0.1',
    description='Unofficial Creon Client',
    url='https://github.com/Golden-Goose-Lab/creon',
    author='Golden-Goose-Lab',
    py_modules=['creon'],
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
    ]
)
