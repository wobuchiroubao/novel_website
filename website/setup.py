# MANIFEST.in syntax:
# include pat1 pat2 ...--add all files matching any of the listed patterns
# graft dir-pattern--add all files under directories matching dir-pattern

from setuptools import setup

with open('README.md', mode='r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    # name='sampleproject'
    # sampleproject--name of project? under which it'll be registered on PyPI
    #
    # and can be installed with:
    # $ pip install sampleproject
    #
    # URL on PyPI: https://pypi.org/project/sampleproject/
    #
    # valid project name specification:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='novel_website',  # Required
    version='2.0.0',  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='Website for your lovely novels~',  # Optional

    # Get the long description from the README file
    long_description=long_description,  # Optional

    # this is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    ### long_description=long_description,  # Optional

    # here long_description is in Markdown
    # valid values are text/plain, text/x-rst, and text/markdown
    long_description_content_type='text/markdown',  # Optional (see note above)

    # This should be a valid link to your project's main homepage.
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    # url='https://github.com/wobuchiroubao/novel_website',  # Optional

    # to specify packages directories (manually)
    packages=['website'],  # Required

    # specify which Python versions project supports.
    # 'pip install' will check this and refuse to install the project
    # if the version does not match.
    python_requires='>=3.6, <4',

    # this field lists other packages that your project depends on to run.
    # any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    install_requires=['flask', 'psycopg2'],  # Optional

    # this tells setuptools to install any data files it finds in your packages.
    # The data files must be specified via the distutils' MANIFEST.in file.
    include_package_data=True
)
