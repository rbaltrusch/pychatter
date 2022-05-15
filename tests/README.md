# Setup tests

To install all dependencies, run:

    cd tests
    python -m pip install -r requirements.txt

# How to run tests

Run tests using the run_tests.py module:

    cd tests
    python run_tests.py

# Code coverage

Code coverage does not work correctly for all threads running pytest directly. Instead, run coverage using the following commands:

```
python -m coverage run --concurrency=thread --rcfile .coveragerc -m py.test
python -m coverage report -m
```

## Options

A number of other options are available:

    usage: run_tests.py [-h] [--debug] [--no-keep] [--no-open]

    Unit test interface

    optional arguments:
      -h, --help           show this help message and exit
      --debug, -d          Enables debug mode
      --no-keep, -nk       Removes test report after showing
      --no-open, -no       Suppresses test report

## Help

To display help for run_tests.py, run the following command:

    python run_tests.py -h
