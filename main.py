import h5py
import numpy
import pyspark as sp
from datetime import datetime

def isWeekend(date):
	day = datetime.strptime(date, '%Y%m%d').weekday()
	# Monday - Sunday
	# 0      - 6
	if day <= 4: 
		return False
	else:
		return True

f1 = h5py.File("BJ16_M32x32_T30_InOut.h5", "r")
f2 = h5py.File("BJ_Meteorology.h5", "r")

# Transform a datasets in a .h5 file into an numpy array.

timeslots = f1["date"][:]
# A array of shape 7220x1 where date[i] is the time of i-th timeslot.

data = f1["data"][:]
# An array of shape 7220x2x32x32 where the first dimension represents the index of timeslots. data[i][0] is a (32, 32) inflow matrix and data[i][1] is a (32, 32) outflow matrix.

temperature = f2["Temperature"][:]
# An array of shape 7220x1 where temperature[i] is the temperature at i-th timeslot.

weather = f2["Weather"][:]
# An array of shape 7220x17 where weather[i] is a one-hot vector which means:
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] Sunny
# [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] Cloudy
# [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] Overcast
# [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] Rainy
# [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] Sprinkle
# [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] ModerateRain
# [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] HeavyRain
# [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0] Rainstorm
# [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0] Thunderstorm
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0] FreezingRain
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0] Snowy
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0] LightSnow
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0] ModerateSnow
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0] HeavySnow
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0] Foggy
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0] Sandstorm
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1] Dusty

windspeed = f2["WindSpeed"][:]
# An array of shape 7220x1 where windspeed[i] is the wind speed at i-th timeslot.

# print('\n')
# print(date[7219])
# print(temperature[7219])
# print(weather[7219])
# print(data[0][0])
# print(windspeed[7219])

for i in range(7220):
	timeslot = timeslots[i].decode('utf8')
	date = timeslot[:8]
	print(date)
	

# rdd = sc.parallelize([[1, 5, b'20160506', 7.2], [2, 1, b'20160925', 105.9], [1, 15, b'20171225', 2.5], [9, 25, b'20170808', 7.5]], 10)
# sc = sp.SparkContext()
# rdd = sc.parallelize([[1, 5, b'20160506', 7.2], [2, 1, b'20160925', 105.9], [1, 15, b'20171225', 2.5], [9, 25, b'20170808', 7.5]])

f1.close()
f2.close()
