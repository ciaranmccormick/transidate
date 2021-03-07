[![PyPI version](https://badge.fury.io/py/transidate.svg)](https://badge.fury.io/py/transidate)
[![Build Status](https://github.com/ciaranmccormick/transidate/workflows/test/badge.svg?branch=master&event=push)](https://github.com/ciaranmccormick/transidate/actions?query=workflow%3Atest)
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

## Using Transidate

Transidate comes with a help guide to get you started. This will list all the options as
well as the transit data formats that are supported.

```sh
transidate --help
```

To validate a data source just specify the path to the data and the schema to validate
the data against. If the `--version` is not specified the data is automatically
validated again TransXChange v2.4.


```sh
transidate circular.xml --version TXC2.4
```

[Validation](imgs/txc24_no_errors.png)

If transidate finds any schema violations it will print the details of the violation
such as the file it occurred in, the line number of the violation and details.

You can also use transidate to validate a archived collection of files.

```sh
transidate all_uk_txc_2_4.zip --version TXC2.4
```

This is iterate over each XML file contained within the zip and collate all the
violations.

[Errors](imgs/txc24_no_errors.png)

Transidate also allows you to export any violations to CSV using the `--csv` flag.

```sh
transidate all_uk_txc_2_4.zip --version TXC2.4 --csv
```
