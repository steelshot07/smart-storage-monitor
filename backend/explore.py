import pandas as pd
import os

folder = 'data/data_Q4_2025'  # change this to match your exact folder name
files = os.listdir(folder)
df = pd.read_csv(f'{folder}/{files[0]}')
print(df.columns.tolist())
print(df.shape)
