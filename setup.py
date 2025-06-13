# setup.py
from setuptools import setup

setup(
    name="virtual-ta",
    version="0.1",
    install_requires=[
        "flask",
        "openai",
        "numpy",
        "pyyaml",
        "faiss-cpu",
        "pillow"
    ],
)
