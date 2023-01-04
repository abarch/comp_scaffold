import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd

df = pd.read_csv('participants_proc2.csv')
df.iloc[:,range(4,46,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(4, 46, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)

plt.figure()
df.iloc[:,range(5,46,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(5, 46, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)

plt.figure()
df.iloc[:,range(6,46,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(6, 46, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)

#######################
plt.figure()
df.iloc[:,range(47,82,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(47, 82, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)

plt.figure()
df.iloc[:,range(48,82,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(48, 82, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)

plt.figure()
df.iloc[:,range(49,82,3)].mean().plot(kind='bar')
for n in range(len(df)):
    df.iloc[n, range(49, 82, 3)].plot(rot=90)
plt.subplots_adjust(bottom=0.4)
# print('hi')

plt.show()