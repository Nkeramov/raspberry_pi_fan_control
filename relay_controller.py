import sys
import time
import argparse
import RPi.GPIO as GPIO
from datetime import datetime


FAN_PIN = 4


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Control a fan based on CPU temperature.")
    parser.add_argument("--lower", type=int, default=40, help="Lower temperature threshold in Celsius (default: 40)")
    parser.add_argument("--upper", type=int, default=45, help="Upper temperature threshold in Celsius (default: 45)")
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


if __name__ == "__main__":
    args = parse_args()
    lower_threshold = args.lower
    upper_threshold = args.upper
    update_delay = args.delay

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, 0)

    try:
        while True:
            try:
                with open('/sys/class/thermal/thermal_zone0/temp') as file:
                    temp = int(float(file.read()) / 1000)
            except FileNotFoundError:
                print("Error: Could not read temperature file. Check if thermal_zone0 exists.", file=sys.stderr)
                GPIO.cleanup()
                sys.exit(1)
            except ValueError:
                print("Error: Could not parse temperature value.", file=sys.stderr)
                GPIO.cleanup()
                sys.exit(1)
            if temp >= upper_threshold:
                GPIO.output(FAN_PIN, 1)
            elif temp < lower_threshold:
                GPIO.output(FAN_PIN, 0)
            stime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            print(f"{stime}  Temperature = {temp} \xb0C, Fan {'ON' if GPIO.input(FAN_PIN) else 'OFF'}")
            time.sleep(update_delay)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        GPIO.cleanup()
        sys.exit(1)
