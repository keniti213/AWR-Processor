
def removeIntel0(x):
    if x.startswith('INTEL') and x[-2:].strip() == '0':
        return x[:-2]
    else:
        return x


def parseProcessor(row):

    try:
        f=row.split(' ')
    except:
        return 'none'

    r=[]

    for i in range(4):
        if len(f) >= i + 1:
            r.append(f[i])
        else:
            r.append('')

    if r[1] == '': r[1] = r[0]

    return r[0] + '__' + r[1] + '__' + r[2] + '__' + "string_total_cpu_cores"


str = "Intel Xeon CPU E5-2650 0 @ 2.00GHz"

str2 = removeIntel0(str)

str3 = parseProcessor(str2)

print(str3)

numbr = 10

print(~True)