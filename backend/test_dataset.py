import pandas as pd
import matplotlib.pyplot as plt
file_path = "../dataset/credit_data.xlsx"

df = pd.read_excel(file_path)

print("Dataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())

print("\nTarget Values:")
print(df["creditScore"].value_counts())

print("\nMissing Values:")
print(df.isnull().sum())