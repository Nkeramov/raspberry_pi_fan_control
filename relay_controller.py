import sys
import time
import argparse
import RPi.GPIO as GPIO
from datetime import datetime
from contextlib import contextmanager


FAN_PIN = 4


def parse_args():
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
def gpio_manager():
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FAN_PIN, GPIO.OUT)
        yield
    finally:
        GPIO.cleanup()


def read_temperature() -> float:
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as file:
            return round(float(file.read()) / 1000, 1)
    except FileNotFoundError:
        handle_error("Could not read temperature file. Check if thermal_zone0 exists.")
    except ValueError:
        handle_error("Could not parse temperature value.")


def handle_error(message, exit_code=1):
    logging.error(message)
    GPIO.cleanup()
    sys.exit(exit_code)


if __name__ == "__main__":
    args = parse_args()
    lower_threshold = args.lower
    upper_threshold = args.upper
    update_delay = args.delay

    with gpio_manager():
        GPIO.setup(FAN_PIN, GPIO.OUT)
        GPIO.output(FAN_PIN, 0)
        try:
            while True:
                temp = read_temperature()
                if temp >= upper_threshold:
                    GPIO.output(FAN_PIN, 1)
                elif temp < lower_threshold:
                    GPIO.output(FAN_PIN, 0)
                stime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                print(f"{stime}  Temperature = {temp} \xb0C, Fan {'ON' if GPIO.input(FAN_PIN) else 'OFF'}")
                time.sleep(update_delay)
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
        except Exception as e:
            handle_error(f"An unexpected error occurred: {e}")
