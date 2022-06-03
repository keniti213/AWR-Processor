import pandas as pd 


data = {'a': [1.0,2.3,3.6,4.8], 'b': [2,3,4,5]}

df1 = pd.DataFrame(data)

print(df1)

max1 = pd.to_numeric(df1['a']).max()

print(max1)

vetor = ''

dado = vetor if vetor != '' else ''

print(dado)