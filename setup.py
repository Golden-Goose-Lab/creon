from setuptools import setup


def get_requirements():
    with open('./requirements.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]


setup(
    name='creon',
    version='0.1.1',
    description='Unofficial Creon Client',
    url='https://github.com/Golden-Goose-Lab/creon',
    author='Golden-Goose-Lab',
    py_modules=['creon'],
    install_requires=get_requirements(),
    classifiers=[
        'Intended Audience :: Developers',
    ]
)
