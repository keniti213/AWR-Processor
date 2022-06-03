import pandas as pd
import numpy as np

df_base = pd.DataFrame(columns=["A", "B", "C"])

print(df_base)

line1 = { "A" : 10, "B" : 20, "C" : 30}
line2 = { "A" : 40, "B" : 50, "C" : 60}

df1 = pd.DataFrame(line1, index=[1])
df2 = pd.DataFrame(line2, index=[1])

df_base = pd.concat([df_base, df1], axis=0)

print(df_base)

df_base = pd.concat([df_base, df2], axis=0)

print(df_base)