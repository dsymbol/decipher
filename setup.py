from setuptools import setup, find_packages

setup(
    name='decipher',
    url='https://github.com/dsymbol/decipher',
    author='dsymbol',
    install_requires=[
        'openai-whisper==20230124',
        'click==8.1.3'
        'ffpb==0.4.1'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'decipher = decipher.__main__:main'
        ]
    }
)
