import pandas as pd 
import numpy as np 

data = {'inst' : [7, 8, 7, 8, 7, 8], 'col1' : [10, 20, 30, 40, 50, 60], 'col2' : [1, 2, 3, 4, 5, 6]}

df = pd.DataFrame(data)

df2 = df.iloc[0]

instancia = df2['inst']

print(df)
print(type(instancia), type(df.iloc[1]['inst']))

