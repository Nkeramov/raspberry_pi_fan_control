import sys
import time
import argparse
import RPi.GPIO as GPIO
from datetime import datetime


FAN_PIN = 4


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Control a fan based on CPU temperature.")
    parser.add_argument("--temp", type=int, default=45, help="Target temperature in Celsius (default: 45)")
    parser.add_argument("--dmin", type=int, default=25, help="Minimum duty cycle [0; 100] (default: 25)")
    parser.add_argument("--p", type=float, default=2.5, help="Proportionality coefficient (default: 2.5)")
    parser.add_argument("--delay", type=int, default=5, help="Update interval in seconds (default: 5)")
    args = parser.parse_args()
    if args.temp <= 0:
        print("Error: temperature must be positive", file=sys.stderr)
        sys.exit(1)
    if args.dmin < 0 or args.dmin > 100:
        print("Error: minimum duty cycle must be in range [0; 100]", file=sys.stderr)
        sys.exit(1)
    if args.p <= 0:
        print("Error: proportionality coefficient must be positive", file=sys.stderr)
        sys.exit(1)
    if args.delay <= 0:
        print("Error: delay must be greater than 0", file=sys.stderr)
        sys.exit(1)
    return args


if __name__ == "__main__":
    args = parse_args()
    target_temp = args.temp
    min_duty_cycle = args.dmin
    max_duty_cycle = 100
    p = args.p
    update_delay = args.delay

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    GPIO.setup(FAN_PIN, GPIO.OUT)
    fan = GPIO.PWM(FAN_PIN, 100)
    fan.start(0)

    duty_cycle = min_duty_cycle

    try:
        while True:
            try:
                with open('/sys/class/thermal/thermal_zone0/temp') as file:
                    temp = round(float(file.read()) / 1000, 1)
                    duty_cycle = round(duty_cycle + p * (temp - target_temp), 1)
                    duty_cycle = max(min_duty_cycle, min(duty_cycle, max_duty_cycle))
                    stime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    print(f"{stime}   Temperature = {temp} \xb0C, Fan duty cycle {duty_cycle} %")
                    fan.ChangeDutyCycle(duty_cycle)
                    time.sleep(update_delay)
            except FileNotFoundError:
                print("Error: Could not read temperature file. Check if thermal_zone0 exists.", file=sys.stderr)
                GPIO.cleanup()
                sys.exit(1)
            except ValueError:
                print("Error: Could not parse temperature value.", file=sys.stderr)
                GPIO.cleanup()
                sys.exit(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        GPIO.cleanup()
        sys.exit(1)

