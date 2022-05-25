[![Unit tests](https://github.com/rbaltrusch/LocalChat/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/rbaltrusch/LocalChat/actions/workflows/pytest-unit-tests.yml)
[![Pylint](https://github.com/rbaltrusch/LocalChat/actions/workflows/pylint.yml/badge.svg)](https://github.com/rbaltrusch/LocalChat/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# LocalChat

LocalChat is a direct chat tool, which may be run to communicate over a local network.

![Gif of the application GUI](https://github.com/rbaltrusch/LocalChat/blob/master/localchat/gui/media/gif1.gif?raw=true "Gif of the application GUI")

Communication happens over the localhost port 8080.

This is primarily an exercise in duplex client-server communication using websockets.

## Getting started

To get a copy of this repository, simply open up git bash in an empty folder and use the command:

    $ git clone https://github.com/rbaltrusch/localchat

To install all python dependencies, run the following in your command line:

    python -m pip install -r requirements.txt

To run the application, run the package from the root repository directory:

    python -m localchat

Hosting a chat server can be done directly inside the graphical user interface, or a dedicated server may be started from the command line using:

    python -m localchat --server

## Configuration

The chat application supports external configuration files. Place a file named config.json in the directory from which the application is run.

The configuration file currently supports one setting, `"chat_format"`, which is used to display chat messages. It supports the following placeholder strings:

- `%T`: time
- `%U`: user name
- `%M`: message

An example config.json could contain the following data:
```json
{
	"chat_format": "%T: %U: %M"
}
```

### Tests

To run tests, change to the tests directory, then run run_tests.py:

```
cd tests
python run_tests.py
```

## Contributions

To contribute to this repository, please read the [contribution guidelines](CONTRIBUTING.md).

## Python

Written in Python 3.7.3.

## License

This repository is open-source software available under the [MIT License](https://github.com/rbaltrusch/localchat/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.

# Attributions

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>.</div>
