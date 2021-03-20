[![PyPI version](https://badge.fury.io/py/transidate.svg)](https://badge.fury.io/py/transidate)
[![test](https://github.com/ciaranmccormick/transidate/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ciaranmccormick/transidate/actions/workflows/test.yaml)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ciaranmccormick/transidate/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)
[![codecov](https://codecov.io/gh/ciaranmccormick/transidate/branch/develop/graph/badge.svg?token=I3693DR0S9)](https://codecov.io/gh/ciaranmccormick/transidate)


# Transidate

Transidate is a commandline tool for validating transit data files such as TransXChange
NeTEx and SIRI.

Transidate can validate several transit data formats out of the box.

## Compatibility

Transidate requires Python 3.7 or later.


## Installing

Install transidate using `pip` or any other PyPi package manager.

```sh
pip install transidate
```

## Validate an XML file

Transidate comes with a help guide to get you started. This will list all the options as
well as the transit data formats that are supported.

```sh
transidate --help
```

To validate a data source just specify the path to the data and the schema to validate
the data against. If the `--version` is not specified the data is automatically
validated again TransXChange v2.4.

```sh
transidate --version TXC2.4 linear.xml
```

![XML with no violations](https://raw.githubusercontent.com/ciaranmccormick/transidate/main/imgs/transidategoodfile.gif)
If transidate finds any schema violations it will print the details of the violation
such as the file it occurred in, the line number of the violation and details.

![XML with violations](https://raw.githubusercontent.com/ciaranmccormick/transidate/main/imgs/transidatebadfile.gif)
## Validate many files at once

You can also use transidate to validate a archived collection of files.

```sh
transidate --version TXC2.4 routes.zip
```

![Zip with no violations](https://raw.githubusercontent.com/ciaranmccormick/transidate/main/imgs/transidategoodzip.gif)
This will iterate over each XML file contained within the zip and collate all the
violations.

![Zip with violations](https://raw.githubusercontent.com/ciaranmccormick/transidate/main/imgs/transidatebadzip.gif)
## Export violations to CSV

Schema violations can be saved to a CSV file using the `--csv` flag.

```sh
transidate --version TXC2.4 --csv routes.zip
```
