import os
from setuptools import setup, find_packages


current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="paramify",
    version="0.1.4",
    description="A lightweight Python library for dynamic parameter management and runtime configuration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ali PAikan",
    author_email="ali.paikan@gmail.com",
    url="https://github.com/luxai-qtrobot/paramify",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0.0",
        "pydantic>=1.10.0",
        "ruamel.yaml>=0.17.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.7",
    license="MIT",
    keywords="parameter management configuration dynamic runtime UI",
    project_urls={
        "Documentation": "https://github.com/luxai-qtrobot/paramify#readme",
        "Source": "https://github.com/luxai-qtrobot/paramify",
        "Tracker": "https://github.com/luxai-qtrobot/paramify/issues",
    },
)
