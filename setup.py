import setuptools

setuptools.setup(
    name="ccb",
    version="0.0.2",
    author="Doron Bergman",
    author_email="doron.bergman@pge.com",
    description="Python wrapper functions for the MaxEnt java program",
    long_description_content_type="text/markdown",
    url="https://github.com/doronator-pge/ccb",
    packages=['ccb'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)