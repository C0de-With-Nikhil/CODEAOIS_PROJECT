from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="codeaois", 
    version="0.3.0",
    author="Nikhil Nagar", 
    description="An advanced, multi-agent AI Developer OS with zero-setup cloud architecture.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
        "requests>=2.25.0"
    ],
    entry_points={
        "console_scripts": [
            "codeaois=codeaois.cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
)
