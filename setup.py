from setuptools import setup, find_packages  # type: ignore

DESCRIPTION = "Python Ragic API client for data loading and manipulation."

# python3 setup.py sdist bdist_wheel
# twine upload --skip-existing dist/* --verbose

VERSION = "0.1.1"

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

core_dependencies = [
    "python-dotenv==0.21.0",
    "PyYAML==6.0.2",
    "httpx[http2]==0.28.1",
    "h2==4.2.0",
]

setup(
    name="python_ragic",
    version=VERSION,
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="jonah_whaler_2348",
    author_email="jk_saga@proton.me",
    license="GPLv3",
    install_requires=core_dependencies,
    keywords=["ragic", "data loader"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.10",
    ],
)
