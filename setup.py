# setup.py
from setuptools import setup, find_packages

setup(
    name="codeaois",
    version="0.1.0",
    description="Advanced AI Developer OS",
    author="CodeAOIS Team",
    packages=find_packages(), # Automatically finds the 'codeaois' directory
    install_requires=[
        # We will add things like 'requests' or 'rich' here later
    ],
    entry_points={
        "console_scripts": [
            # This maps the global command 'codeaois' to the 'main()' function inside codeaois/cli/main.py
            "codeaois=codeaois.cli.main:main",
        ],
    },
    python_requires=">=3.8",
)