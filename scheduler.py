# Checks whether it's time to remind
from datetime import datetime, timedelta



FORGETTING_CURVE = [  
    10,     60,     # calculated in minutes
    1440,   1440*3,
    1440*7, 1440*14,
]

FORGETTING_CURVE_TIME = [
    '10 minutes', '1 hour',
    '1 day', '3 days',
    '7 days', '14 days'
]



# THE NEXT TIME OF REPEATING
def next_time_to_repeat(step):
    return datetime.now() + timedelta(minutes=FORGETTING_CURVE[step])