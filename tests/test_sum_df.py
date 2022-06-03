import pandas as pd 
import numpy as np 

data = {'A': [10, 2, 5, 15, 8], 'B':[5, 7, 15, 3, 25] }

df = pd.DataFrame(data)

print(df)
df['A'] = df['A'].astype(float)
df['B'] = df['B'].astype(float)

sum_df_max = (df['A'] + df['B']).max()

print(sum_df_max)