source .venv/bin/activate
# specify parameters as desired
# python3 relay_controller.py --lower 35 --upper 40 --delay 5
python3 proportional_controller.py --temp 45 --delay 5 --p 3 --dmin 30
