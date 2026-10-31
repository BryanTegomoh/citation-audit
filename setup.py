"""Setup script for Citation Audit."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    # Runtime deps only: stop at the development section.
    requirements = []
    for line in fh:
        if "Development dependencies" in line:
            break
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="citation-audit",
    version="1.0.0",
    author="Bryan Tegomoh",
    description="Detect and fix citation errors in academic literature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BryanTegomoh/citation-audit",
    # src/ is the citation_toolkit package (it uses relative imports).
    packages=["citation_toolkit"]
    + ["citation_toolkit." + p for p in find_packages(where="src")],
    package_dir={"citation_toolkit": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "citation-verify=citation_toolkit.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "citation_toolkit": ["../data/*.json"],
    },
)
