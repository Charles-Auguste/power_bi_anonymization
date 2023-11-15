from setuptools import find_packages, setup

requirements = """
pip>=21.3.1
setuptools>=56
wheel==0.37.0
pandas<2
numpy
pre-commit
flake8==3.8.3
black==21.9b0
coverage
pyarrow
pytest
pytest-cov
feather-format
plotly
scikit-learn
ipywidgets
widgetsnbextension
matplotlib>=3.4.3
python-dotenv
click==7.1.2
deepdiff
streamlit
openpyxl
termcolor
"""


setup(
    name="powerbi_anonymisation_pkg",
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "write_to": "../version.txt",
        "root": "..",
        "relative_to": __file__,
    },
    author="Charles-Auguste GOURIO",
    author_email="charlesaugustegourio@gmail.com",
    description="{description}",
    packages=find_packages(),
    test_suite="tests",
    install_requires=requirements,
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    zip_safe=False,
    # all functions @cli.command() decorated in powerbi_anonymisation_pkg/cli.py
    entry_points={
        "console_scripts": [
            "powerbi_anonymisation_pkgcli = powerbi_anonymisation_pkg.cli:cli"
        ]
    },
    scripts=["scripts/powerbi_anonymisation_version"],
)
