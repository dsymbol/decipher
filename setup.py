from setuptools import setup, find_packages

setup(
    name='decipher',
    url='https://github.com/dsymbol/decipher',
    author='dsymbol',
    install_requires=[
        'openai-whisper==20230314',
        'tqdm'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'decipher = decipher.__main__:main'
        ]
    }
)
