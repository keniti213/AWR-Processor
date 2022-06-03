import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def transforma(x):

	if x == "0":
		return float(0)

	else:

		y = x[-1]
		x = float(x[0:-1])

		if y == "K" :
			x = x * 1024

		if y == "M" :
			x = x * 1024 * 1024

		if y == "G" :
			x = x * 1024 * 1024 * 1024

		return x


data2 = pd.read_csv("mini_size.txt", names = ["dado"], dtype = str)
print(data2)

data2["dado"] = data2["dado"].apply(transforma)

print(data2)
print(data2.dtypes)
print(data2.describe())

plt.hist(data2["dado"])
plt.xlabel("x")
plt.ylabel("y")
plt.savefig("mini_size.png")
plt.show()
plt.close()