"""Setup for PyPi

Used for setting up MuGen

"""

from distutils import setup
setup(
    name='MuGen',
    version='1.0',
    author='Spencer Kemp',
    author_email='snkemp@stetson.edu',
    url='https://gitbub.com/snkemp',
    description='Music Generation with Machine Learning',
    long_description=open('README.md', 'r').read(),
    packages=['src']
    )
