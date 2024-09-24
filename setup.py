import setuptools

# Open the README.md file and read its content into the 'long_description' variable.
with open("Readme.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Define the version of the package.
__version__ = "0.0.1"

# Setup function to define the package details.
setuptools.setup(
    name="translator",                     # The name of the overall project package.
    version=__version__,                   # Version of the project.
    author="puzan789",                     # Author name.
    author_email="puzan936@gmail.com",     # Author email.
    description="A project with text summarization and API components",  # Short description.
    long_description=long_description,     # Detailed description from README.md.
    long_description_content_type="text/markdown",  # Long description format.
    packages=setuptools.find_packages(where="src"), # Automatically find all packages under 'src/'.
    package_dir={"": "src"},               # Root package directory is 'src'.
    include_package_data=True,             # Include non-Python files specified in MANIFEST.in.
)
