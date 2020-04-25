import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="min-rss",
    version="0.0.3",
    author="Nathan Walsh",
    author_email="nwalsh1995@gmail.com",
    description="A correct and minimal RSS 2.0 generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nwalsh1995/min-rss-gen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
