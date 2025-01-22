import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(4, GPIO.OUT)
fan = GPIO.PWM(4, 100)
fan.start(0)


if __name__ == "__main__":
    min_speed = 20
    lower_threshold = 40
    upper_threshold = 45
    p = 3
    try:
        while True:
            with open('/sys/class/thermal/thermal_zone0/temp') as file:
                temp = int(float(file.read()) / 1000)
                speed = -1
                if temp >= upper_threshold:
                    speed = min_speed + p * (temp - lower_threshold)
                    if speed > 100:
                        speed = 100
                elif temp < 40:
                    speed = 0
                if speed >= 0:
                    print(f"Temperature = {temp} \xb0C, Fan duty cycle = {speed} %")
                    fan.ChangeDutyCycle(speed)
            time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit
