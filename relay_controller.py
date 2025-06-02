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
    parser.add_argument("--lower", type=int, default=45, help="Lower temperature threshold in Celsius (default: 45)")
    parser.add_argument("--upper", type=int, default=50, help="Upper temperature threshold in Celsius (default: 50)")
    parser.add_argument("--delay", type=int, default=5, help="Update interval in seconds (default: 5)")
    args = parser.parse_args()
    if args.lower <= 0:
        print("Error: lower must be positive", file=sys.stderr)
        sys.exit(1)
    if args.upper <= 0:
        print("Error: upper must be positive", file=sys.stderr)
        sys.exit(1)
    if args.lower >= args.upper:
        print("Error: lower must be less than upper", file=sys.stderr)
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
    lower_threshold = args.lower
    upper_threshold = args.upper
    update_delay = args.delay
    pin_state = 0
    with gpio_manager():
        GPIO.setup(FAN_PIN, GPIO.OUT)
        GPIO.output(FAN_PIN, pin_state)
        try:
            while True:
                if (temperature := read_temperature()) is not None:
                    new_pin_state = pin_state
                    if temperature >= upper_threshold:
                        new_pin_state = 1
                    elif temperature < lower_threshold:
                        new_pin_state = 0
                    if new_pin_state != pin_state:
                        pin_state = new_pin_state
                        GPIO.output(FAN_PIN, pin_state)
                        logger.info(f"Fan pin state changed to {'ON' if pin_state else 'OFF'}")
                    logger.info(f"Temperature = {temperature} \xb0C, Fan pin state {'ON' if pin_state else 'OFF'}")
                time.sleep(update_delay)
        except KeyboardInterrupt:
            logger.info("Exiting...")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            logger.info("Stopping fan...")
            GPIO.output(FAN_PIN, 0)


if __name__ == "__main__":
    main()
