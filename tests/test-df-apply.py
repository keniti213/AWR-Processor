import pandas as pd
import numpy as np

def transforma(x):
	
	y = x[-1]
	
	x = x[0:-1]
	
	x = float(x)

	if y == "K" :
		x = x * 1024
	

	if y == "M" :
		x = x * 1024 * 1024

	if y == "G" :
		x = x * 1024 * 1024 * 1024


	return x


fonte = [["7K"], ["8.5M"], ["1.5G"]]
data1 = pd.DataFrame(fonte, columns=["dado"])

data1["dado"] = data1["dado"].apply(transforma)

data1["dado"] = data1["dado"] * 0.75

print(data1.dtypes)
print(data1)

data2 = pd.read_csv("dados.csv")
print(data2)

data2["dado"] = data2["dado"].apply(transforma)

data2["dado"] = data2["dado"] * 0.75

print(data2)
print(data2.dtypes)