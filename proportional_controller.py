import sys
import time
import logging
import argparse
import RPi.GPIO as GPIO
from datetime import datetime
from argparse import Namespace
from typing import Iterator, Optional
from contextlib import contextmanager


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s : %(levelname)s : %(funcName)s : %(lineno)s : %(message)s",
    datefmt="%H:%M:%S"
)

FAN_PIN = 4


def parse_args() -> Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Control a fan based on CPU temperature.")
    parser.add_argument("--temp", type=int, default=45, help="Target temperature in Celsius (default: 45)")
    parser.add_argument("--dmin", type=int, default=25, help="Minimum duty cycle [0; 100] (default: 25)")
    parser.add_argument("--dmax", type=int, default=100, help="Maximum duty cycle [0; 100] (default: 100)")
    parser.add_argument("--p", type=float, default=2.5, help="Proportionality coefficient (default: 2.5)")
    parser.add_argument("--delay", type=int, default=5, help="Update interval in seconds (default: 5)")
    args = parser.parse_args()
    if args.temp <= 0:
        print("Error: temperature must be positive", file=sys.stderr)
        sys.exit(1)
    if args.dmin < 0 or args.dmin > 100:
        print("Error: minimum duty cycle must be in range [0; 100]", file=sys.stderr)
        sys.exit(1)
    if args.dmax < 0 or args.dmax > 100 or args.dmax <= args.dmin:
        print("Error: maximum duty cycle must be greater than minimum duty cycle", file=sys.stderr)
        sys.exit(1)
    if args.p <= 0:
        print("Error: proportionality coefficient must be positive", file=sys.stderr)
        sys.exit(1)
    if args.delay <= 0:
        print("Error: delay must be greater than 0", file=sys.stderr)
        sys.exit(1)
    return args


@contextmanager
def gpio_manager() -> Iterator[None]:
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FAN_PIN, GPIO.OUT)
        yield
    finally:
        GPIO.cleanup()


def read_temperature() -> Optional[float]:
    temperature_file = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(temperature_file, "r") as file:
            temperature_raw = file.read().strip()
            temperature = round(float(temperature_raw) / 1000, 1)
            return temperature
    except ValueError:
        logger.error("Could not parse temperature value from file: {temperature_file}. Raw: {temperature_raw}")
    except FileNotFoundError:
        logger.error(f"Could not read temperature file: {temperature_file}. Check if thermal_zone0 exists")
    return None


def main() -> None:
    args = parse_args()
    p = args.p
    error_threshold = 0.1
    target_temperature = args.temp
    update_delay = args.delay
    min_duty_cycle = args.dmin
    max_duty_cycle = args.dmax
    duty_cycle = min_duty_cycle
    with gpio_manager():
        fan = GPIO.PWM(FAN_PIN, 100)
        fan.start(0)
        try:
            while True:
                if (temperature := read_temperature()) is not None:
                    error = round(temperature - target_temperature, 1)
                    if abs(error) > error_threshold:
                        new_duty_cycle = round(min_duty_cycle + p * error)
                        new_duty_cycle = max(min_duty_cycle, min(duty_cycle, max_duty_cycle))
                        if new_duty_cycle != duty_cycle:
                            duty_cycle = new_duty_cycle
                            fan.ChangeDutyCycle(duty_cycle)
                            logger.info(f"Fan duty cycle changed to {duty_cycle}%")
                    logger.info(f"Temperature = {temperature} \xb0C, Error = {error} \xb0C, Fan duty cycle {duty_cycle} %")
                time.sleep(update_delay)
        except KeyboardInterrupt:
            logger.info("Exiting...")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            if 'fan' in locals() and fan is not None:
                logger.info("Stopping fan...")
                fan.stop()


if __name__ == "__main__":
    main()
