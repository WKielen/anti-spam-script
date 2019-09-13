import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="antispamscript",
    version="0.0.1",
    author="Wim Kielen",
    author_email="wim_kielen@hotmail.com",
    description="A small script to remove spam from a mailbox.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wkielen/mail-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'antispamscript=antispamscript.antispamscript:main',
        ],
    }
)
