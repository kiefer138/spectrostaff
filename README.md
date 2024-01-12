# overview

spectrostaff is an application for visualizing music

## getting Started

this guide will help you set up your development environment for the `spectrostaff` project

### prerequisites

ensure you have the following installed on your machine:

- Git
- Make
- Poetry
- Python 3.11

### installing

1. **clone the repository**: use the following command to clone the `develop` branch of the `spectrostaff` repository:

    ```bash
    git clone -b develop https://github.com/kiefer138/spectrostaff
    ```

2. **navigate to the project directory**:

    ```bash
    cd spectrostaff
    ```

3. **install the project in development mode**: this will install all the dependencies you need for development

    ```bash
    make install
    ```

## documentation

build the documentation:

    ```bash
    make docs 
    ```

view the documentation:

    ```bash
    make view-docs
    ```

## running the tests

run the tests:

    ```bash
    make test
    ```

## building the project

build the project using the following command:

    ```bash
    make build
    ```

## cleaning the project

clean the project using the following command:

    ```bash
    make clean
    ```

## help

display help information with the following command:

    ```bash
    make help
    ```

## authors

- Tyler Evans

## license

this project is licensed under the [MIT License](https://opensource.org/licenses/MIT)
