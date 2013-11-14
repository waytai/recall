from setuptools import setup, find_packages

with open("VERSION") as fp:
    version = fp.read()

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name='recall',
    version=version,
    description='CQRS Library for Python',
    long_description=long_description,
    author='Doug Hurst',
    author_email='dalan.hurst@gmail.com',
    maintainer='Doug Hurst',
    license='MIT',
    url='https://github.com/dalanhurst/recall',
    packages=find_packages(exclude=['example', 'tests']),
    download_url='http://pypi.python.org/packages/source/r/recall/recall-%s.tar.gz' % version,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries"]
)
