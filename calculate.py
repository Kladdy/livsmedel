from data_extractor import NutritionDataSource, NutritionContent, solve_for_recipe

# Define variables
filepath = "data/LivsmedelsDB_202304122217.xlsx"

# Create a NutritionDataSource object
data = NutritionDataSource(filepath, header=2)

# Define list of ingridients
ingridients = ["mjölk", "vetemjöl", "ägg", "rapsolja", "salt"]
df_nutrition = data.get_nutrition_data(ingridients)

# Query content
content = NutritionContent(data)
content_dict = content.query_neutrition_content()

# Solve for the recipe
x = solve_for_recipe(df_nutrition, content_dict)

# Print the result
# Get the maximum width of the ingridient names
max_width = max([len(ingridient_name) for ingridient_name in df_nutrition["Livsmedelsnamn"]])
print(f"För varje 100 g av produkten behöver du:")
for i in range(len(ingridients)):
    # Get the name of the ingridient
    ingredient_name = df_nutrition["Livsmedelsnamn"][i]
    # Pad the name with spaces to make it the same width as the longest name
    ingredient_name = f"{ingredient_name}:".ljust(max_width+1)
    print(f" • {ingredient_name} {100*x[i]:.2g} g") # 100* as the result is in factor of 100 g

print(f"\nDetta ger följande näringsinnehåll per 100 g av produkten:")
# Get the maximum width of the nutrient names
max_width = max([len(nutrient_name) for nutrient_name in content_dict.keys() if content_dict[nutrient_name] is not None])
for idx, (nutrient_to_specify, nutrient_amount) in enumerate(content_dict.items()):
    if nutrient_amount is None:
        continue
    
    # Pad the name with spaces to make it the same width as the longest name
    nutrient_to_specify_name = f"{nutrient_to_specify}:".ljust(max_width+1)

    # Calculate the amount of the nutrient in the product
    nutrient_amount = sum([x[i]*float(df_nutrition[nutrient_to_specify][i]) for i in range(len(ingridients))])
    nutrient_amount = float(f"{nutrient_amount:.2g}")

    # Get the expected amount of the nutrient
    expected_amount = content_dict[nutrient_to_specify]

    print(f" • {nutrient_to_specify_name} {nutrient_amount}\t (förväntat: {expected_amount})")
print()