import os
import sys
from data_extractor import NutritionDataSource

# Define variables
filepath = "data/LivsmedelsDB_202304122217.xlsx"

# Create a NutritionDataSource object
data = NutritionDataSource(filepath, header=2)
print(data.df.head())

# Define list of ingridients
ingridients = ["mjölk", "vetemjöl", "ägg", "rapsolja", "salt"]
data.get_nutrition_data(ingridients)