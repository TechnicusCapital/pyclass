import sys
from datetime import datetime, time, date, timedelta

# def main():

#     dt = datetime.now()
#    #utc = datetime.utcnow()
#     time_string = dt.strftime("%X")

#     for line in sys.stdin:
#         data = line.strip().split("\t")
#         if len(data) == 6:
#             _date, _time, store, item, cost, payment = data          
#             d = f"{dt}\t{time_string}\t{store}\t{item}\t{cost}\t{payment}"
#             print(d)
# main()


dt = datetime.now()
delta_min = timedelta(seconds = 60)
delta_years = timedelta(weeks = 104)
new_dt = dt - delta_min
dt_add_years = dt + delta_years


time_delta = timedelta(days=100, hours=10, minutes=13)
print(time_delta)

def _function(feet, inches, td_object):
    print(f"Height: {feet}'{inches} after {td_object}")

_function(5, 8, time_delta)