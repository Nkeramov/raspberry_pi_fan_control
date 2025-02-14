source .venv/bin/activate
# specify parameters as desired
#python3 relay_controller.py --lower 40 --upper 45 --delay 5
python3 proportional_controller.py --temp 45 --delay 5 --p 15.0 --dmin 55 --dmax 100
