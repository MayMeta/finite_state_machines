![README_Header.jpg](README_Header.jpg)

# Finite-State Machines

This framework provides a pure-Python implementation of
[Finite-State Machines](https://en.wikipedia.org/wiki/Finite-state_machine) -
simple and useful graph-like computational models.

Main code file can be found here: [fsm.py](finite_state_machines/fsm.py)  
A toy problem definition can be found here: [ToyProblem.md](examples/ToyProblem.md)  

## Setting Up the Development Environment

To set up the development environment, you'll need to clone the repository and install necessary dependencies using
Poetry.

### Prerequisites

- Python >= 3.10
- Poetry >= 1.7

### Steps

1. **Clone the repository:**

    ```sh
    git clone git@github.com:MayMeta/ebay_assignment_dev.git
    cd ebay_assignment_dev
    ```

2. **Install Poetry (if not already installed):**

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install the dependencies:**

    ```sh
    poetry install --only main
    ```

4. **Activate the virtual environment:**

    ```sh
    poetry shell
    ```

Your development environment is now set up and ready to use.

## Building the Package

To build the package, follow these steps:

1. **Ensure you are in the root directory of the repository:**

    ```sh
    cd ebay_assignment_dev
    ```

2. **Build the package:**

    ```sh
    poetry build
    ```

The built package files will be located in the `dist/` directory.

## Installing the Package in Another Virtual Environment

To install the built package in a different virtual environment, follow these steps:

1. **Navigate to the directory where the built package files are located:**

    ```sh
    cd ebay_assignment_dev/dist
    ```

2. **Create a new virtual environment:**

    ```sh
    python3 -m venv new_env
    source new_env/bin/activate  # On Windows use `new_env\Scripts\activate`
    ```

3. **Install the package:**

    ```sh
    pip install finite_state_machines-0.1.0-py3-none-any.whl
    ```

## Development

To set up the development environment with all necessary dependencies, including development dependencies, use:

```sh
poetry install --with dev
 ```

## Formatting Code
- Ensure that your code is properly formatted before committing. Use the provided script to format your code:

```sh
poetry run bash format-code.sh finite_state_machines/
```

##  Running Tests

To install the test dependencies, use:

```sh
poetry install --with test
poetry run pytest
```
