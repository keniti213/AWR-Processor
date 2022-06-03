import pandas as pd 


#data = {'host': ['host1','host2','host3','host4', 'host5', 'host6'], 'data': [1,2,3,4,5,6]}

def getShortDBVersion(db_version):
    major_version = db_version.split('.')
    versions = { '19': '19c', '18': '18c', '12': '12c',
        '11': '11g', '10': '10g', '9': '9i', 'n/a': ''}
    return versions[str(major_version[0])]

lista = { '19': '19c', '18': '18c', '12': '12c',
    '11': '11g', '10': '10g', '9': '9i', 'n/a': ''}

version = '18.0.0.0.0'

print(getShortDBVersion(version))

for k in lista:
	print(k)