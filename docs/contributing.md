# Contributing

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

## Structure

- [trady](/trady/) (code);
  - [datatypes](/trady/datatypes/) (exchange datatypes);
  - [exchanges](/trady/exchanges/) (exchange implementations);
  - [interface.py](/trady/interface.py) (abstract exchange interface);
  - [settings.py](/trady/settings.py) (abstract exchange settings);

## Implementing an Exchange

1. Create a package in [`trady.exchanges`](/trady/exchanges/);
2. Implement interface by subclassing [`ExchangeInterface`](/trady/interface.py);
3. Define settings by subclassing [`ExchangeSettings`](/trady/settings.py);
