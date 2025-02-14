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
    p = args.p
    error_threshold = 0.1
    target_temp = args.temp
    update_delay = args.delay
    min_duty_cycle = args.dmin
    max_duty_cycle = args.dmax
    duty_cycle = min_duty_cycle

    with gpio_manager():
        fan = GPIO.PWM(FAN_PIN, 100)
        fan.start(0)
        try:
            while True:
                temp = read_temperature()
                error = round(temp - target_temp, 1)
                if abs(error) > error_threshold:
                    duty_cycle = round(min_duty_cycle + p * error)
                    duty_cycle = max(min_duty_cycle, min(duty_cycle, max_duty_cycle))
                    fan.ChangeDutyCycle(duty_cycle)
                stime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                print(f"{stime}   Temperature = {temp} \xb0C, Error = {error} \xb0C, Fan duty cycle {duty_cycle} %")
                time.sleep(update_delay)
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
        except Exception as e:
            handle_error(f"An unexpected error occurred: {e}")
