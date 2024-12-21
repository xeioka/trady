# Contributing

## Requirements

1. [Python](https://www.python.org) >= 3.12;

## Setup

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

## Project Structure

- [`trady`](/trady/) (source);
  - [`datatypes`](/trady/datatypes/) (interface datatypes);
  - [`exchanges`](/trady/exchanges/) (interface implementations);
  - [`exceptions.py`](/trady/exceptions.py) (interface exceptions);
  - [`interface.py`](/trady/interface.py) (exchange interface);
  - [`settings.py`](/trady/settings.py) (exchange settings);

## Exchange Implementation

Reference existing implementations for example: [`trady.exchanges`](/trady/exchanges/).

1. Create a dedicated package in [`trady.exchanges`](/trady/exchanges/);
2. Implement interface by subclassing [`ExchangeInterface`](/trady/interface.py);
3. Implement settings by subclassing [`ExchangeSettings`](/trady/settings.py);
