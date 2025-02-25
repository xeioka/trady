# Contributing

## Requirements

- [Python](https://www.python.org) >= 3.12;

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

## Exchange Implementation

1. Create a dedicated package in [`trady.exchanges`](/trady/exchanges/);
2. Implement settings by subclassing [`ExchangeSettings`](/trady/settings.py);
3. Implement interface by subclassing [`ExchangeInterface`](/trady/interface.py);

For an example, reference the [Binance implementation](/trady/exchanges/binance/).
