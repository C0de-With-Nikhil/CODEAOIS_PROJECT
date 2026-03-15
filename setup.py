from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="codeaois", 
    version="0.3.1",
    author="Nikhil Nagar", 
    description="An advanced, multi-agent AI Developer OS with zero-setup cloud architecture.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
install_requires=[
        # --- UI & Core Engine ---
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=1.0.0",
        
        # --- Cloud Sync ---
        "supabase>=2.3.0",
        
        # --- Web Researcher Agent ---
        "duckduckgo-search>=4.0.0",
        "beautifulsoup4>=4.12.0",
        
        # --- Local Brain & /index Memory ---
        "chromadb>=0.4.0",
        "fastembed>=0.2.0"   
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
