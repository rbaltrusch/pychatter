[![Unit tests](https://github.com/rbaltrusch/pychatter/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/rbaltrusch/pychatter/actions/workflows/pytest-unit-tests.yml)
[![Pylint](https://github.com/rbaltrusch/pychatter/actions/workflows/pylint.yml/badge.svg)](https://github.com/rbaltrusch/pychatter/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# pychatter

pychatter is a direct chat tool, which may be run to communicate over a local network.

![Gif of the application GUI](https://github.com/rbaltrusch/pychatter/blob/master/pychatter/gui/media/gif1.gif?raw=true "Gif of the application GUI")

Communication happens over the localhost port 8080.

This is primarily an exercise in duplex client-server communication using websockets.

## Getting started

Install the pychatter package using pip, then run the package:

    python -m pip install pychatter
    python -m pychatter

Hosting a chat server can be done directly inside the graphical user interface, or a dedicated server may be started from the command line using:

    python -m pychatter --server

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

## Contributions

To contribute to this repository, please read the [contribution guidelines](https://github.com/rbaltrusch/pychatter/blob/master/CONTRIBUTING.md).

## Python

Written in Python 3.7.3.

## License

This repository is open-source software available under the [MIT License](https://github.com/rbaltrusch/pychatter/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.

# Attributions

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>.</div>
