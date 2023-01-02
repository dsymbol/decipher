from setuptools import setup, find_packages

setup(
    name='decipher',
    url='https://github.com/dsymbol/decipher',
    author='dsymbol',
    install_requires=[
        'whisper @ git+https://github.com/openai/whisper.git',
        'click==8.1.3',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'decipher = decipher.__main__:main'
        ]
    }
)
