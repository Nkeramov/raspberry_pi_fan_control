# Raspberry Pi fan control

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846.svg?logo=Raspberry-Pi)](https://www.raspberrypi.com/)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![license](https://img.shields.io/badge/licence-MIT-green.svg)](https://opensource.org/licenses/MIT)


This project provides examples of fan control based on the current CPU temperature.

It includes implementations of a relay controller and a proportional controller. 

The fan is connected via a transistor switch to the 4th pin of the I/O ports. The fan connection pin can be changed in scripts. The remaining parameters can be set at startup.

## Setting up project

Install the requirements. To keep things simple, we will use the Python virtual environment.

```bash
        python -m venv .venv
        source .venv/bin/activate           # for Linux and Mac
        ./env/Scripts/activate              # for Windows
        pip install -r requirements.txt
```

Make run.sh executable and use it to run project. Script arguments can be changed in the `run.sh` file.

```bash
        chmod +x run.sh
        ./run.sh
```

## Contributing

We welcome contributions! If you want to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to your fork and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Ref

- [Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi OS](https://www.raspberrypi.com/documentation/computers/os.html)
