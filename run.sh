source .venv/bin/activate
# specify parameters as desired
#python3 relay_controller.py --lower 45 --upper 50 --delay 5
python3 proportional_controller.py --temp 45 --delay 5 --p 15.0 --dmin 50 --dmax 100
