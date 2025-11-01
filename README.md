# Raspberry Pi fan control

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846.svg?logo=Raspberry-Pi)](https://www.raspberrypi.com/)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![license](https://img.shields.io/badge/licence-MIT-green.svg)](https://opensource.org/licenses/MIT)

This project provides examples of fan control based on the current CPU temperature.

It includes implementations of a relay controller and a proportional controller. 

The fan is connected via a transistor switch to the 4th pin of the I/O ports. The fan connection pin can be changed in scripts. The remaining parameters can be set at startup.

## Setting up and running the project
Clone repository:
```bash 
git clone https://github.com/Nkeramov/raspberry_pi_fan_control.git
```
Switch to repo directory
```bash 
cd raspberry_pi_fan_control
```
Сreate new virtual environment:
```bash 
python -m venv .venv 
```
Activate the virtual environment with the command:
```bash 
source .venv/bin/activate
```
Install dependencies from the requirements file:
```bash
pip install -r requirements.txt
```
Run relay fan controller with command (args for example):
```bash
python3 relay_controller.py --lower 45 --upper 50 --delay 5
```
Run proportional fan controller with command (args for example):
```bash
python3 proportional_controller.py --temp 45 --delay 5 --p 15.0 --dmin 50 --dmax 100
```
Or use a launch script `run.sh`, making it executable first
```bash
chmod +x run.sh
```
Script arguments can be changed.

## Adding to startup

You can set up automatic script launch at system startup.

Open the `/etc/rc.local` file in editor:
```bash
sudo nano /etc/rc.local
```
Add to the end of file this line:
```bash
/home/pi/raspberry_pi_fan_control/run.sh &
```
Press Ctrl+O → Enter → Ctrl+X to save and exit.
With these few easy steps, you now have automatic fan control.

## Contributing

If you want to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to your fork and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Ref

- [Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi OS](https://www.raspberrypi.com/documentation/computers/os.html)
