import setuptools

setuptools.setup(
    name="ccb-doronator-for-mac", # Replace with your own username
    version="0.0.1",
    author="Doron Bergman",
    author_email="doron.bergman@pge.com",
    description="Python wrapper functions for the MaxEnt java program",
    long_description="later, gator",
    long_description_content_type="text/markdown",
    url="https://github.com/doronator-pge/ccb",
    # packages=setuptools.find_packages(),
    packages=['ccb'],

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    # package_dir={'': 'ccb'},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    # packages=setuptools.find_packages(where='ccb'),  # Required

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)