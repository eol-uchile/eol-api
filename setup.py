import setuptools

setuptools.setup(
    name="eol_api",
    version="1.1.0",
    author="Oficina EOL UChile",
    author_email="eol-ing@uchile.cl",
    description="A unified API apps that aggregates multiple general-purpose APIs into a single service.",
    url="https://eol.uchile.cl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "lms.djangoapp": ["eol_api = eol_api.apps:EOLAPIConfig"],
    },
)
