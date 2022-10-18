from setuptools import setup

setup(
    name='decipher',
    packages=['decipher'],
    url='https://github.com/dsymbol/decipher',
    license='OSI Approved :: MIT License',
    author='dsymbol',
    author_email='',
    platforms='OS Independent',
    description='Effortlessly add whisper AI generated transcription subtitles into provided video',
    install_requires=[
        'whisper @ git+https://github.com/openai/whisper.git'
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
            'console_scripts': [
                'decipher = decipher.__main__:main'
            ]
        }
)
