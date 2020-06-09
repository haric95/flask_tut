# this file is used to make our project easilly installable on other machines.
# using it, we can create a portable dist file that tells us what to install.

from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    # the packages object tells python which depenencies are required.
    # find_packages() does this automatically for us.
    packages=find_packages(),
    #
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)