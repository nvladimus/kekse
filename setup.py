from setuptools import setup, find_packages

setup(
        name='kekse',
        version='0.1',
        description='Rapid GUI building for instrument control (PyQt based)',
        url='https://github.com/nvladimus/kekse',
        author='Nikita Vladimirov',
        author_email="nvladimus@gmail.com",
        install_requires=[
            'nidaqmx',
            'numpy',
            'PyDAQmx',
            'PyQt5',
            'pyserial'
        ],
        packages=find_packages()
)