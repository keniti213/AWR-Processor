import pandas as pd 


#data = {'host': ['host1','host2','host3','host4', 'host5', 'host6'], 'data': [1,2,3,4,5,6]}

df1 = pd.DataFrame(columns=['env', 'hosts', 'data', 'field'])

rows = [{'env': 'PRD', 'hosts': 'alpha', 'data': 100, 'field': 4}, {'env': 'PRD', 'hosts': 'beta', 'data': 200, 'field': 1000},
{'env': 'PRD', 'hosts': 'gama', 'data': 300, 'field': 200},
{'env': 'PRD', 'hosts': 'alpha', 'data': 150, 'field': 3},
{'env': 'PRD', 'hosts': 'alpha', 'data': 160,'field': 2},
{'env': 'PRD', 'hosts': 'teta', 'data': 400, 'field': 1},
{'env': 'PRD', 'hosts': 'beta', 'data': 250, 'field': 1},
{'env': 'PRD', 'hosts': 'alpha', 'data': 180, 'field': 1},
{'env': 'PRD', 'hosts': 'teta', 'data': 450, 'field': 2000}]

for i in rows:
	df1 = df1.append(i, ignore_index=True)

print(df1)

df1['name'] = ['','', '', '', '', '', '', '', '']

print(df1)

df1 = df1.groupby(['env','hosts'], as_index=False).agg({'data': 'max', 'field': 'sum', 'name': 'first'})
print(df1)
