
# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# This safely reads your README.md to use as the PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="codeaois", 
    version="0.1.0", # Your MVP version!
    author="Nikhil Nagar", # <-- CHANGE THIS to your actual name or handle!
    description="An advanced, multi-agent AI Developer OS for the terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests",
        "prompt_toolkit",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            # This is the magic line! It tells everyone's computer that typing 
            # 'codeaois' in their terminal should launch your main.py file.
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