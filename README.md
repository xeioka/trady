# Trady

[![Linting](https://github.com/xeioka/trady/actions/workflows/linting.yaml/badge.svg)](https://github.com/xeioka/trady/actions/workflows/linting.yaml)

> _Do you have any idea why they call him Franky "Four Fingers", Doug?_

## Requirements

1. [Python](https://www.python.org) >= 3.12;

## Usage

Install from GitHub repository (see [the documentation](https://pip.pypa.io/en/stable/topics/vcs-support/#vcs-support) or run `pip install --help`):

```sh
pip install git+ssh://git@github.com/xeioka/trady.git
```

## Contributing

1. Clone the repository:

    ```sh
    git clone git@github.com:xeioka/trady.git
    cd trady
    ```

2. Create a Python virtual environment and install the requirements:

    ```sh
    python3.12 -m venv .venv && source .venv/bin/activate
    pip install -r requirements/dev.txt
    ```

3. Install pre-commit hooks:

    ```sh
    pre-commit install
    ```
