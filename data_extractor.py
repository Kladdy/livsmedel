import pandas as pd
import numpy as np
import inquirer
import os
import sys
import scipy.optimize as optimize

def warn_sound():
    sys.stdout.write('\a')

# kwargs are passed to the reading of the file
class NutritionDataSource:
    def __init__(self, filepath: str, **kwargs):
        self.filepath = filepath

        # Choices file
        os.makedirs("choices", exist_ok=True)
        self.choices_filename = f"choices/choices_{self.filepath.split('/')[-1]}.csv"

        # Load the data
        if filepath.endswith(".xlsx"):
            self.df = pd.read_excel(filepath, **kwargs)
        else:
            raise ValueError("'filepath' must end with .xlsx")
        
    def get_nutrition_data(self, ingridients: list):
        
        df_nutrition = pd.DataFrame()

        for ingredient in ingridients:
            print(f"\nLetar efter livsmedel som motsvarar '{ingredient}'...")

            # Filter the data
            filtered_data = self.df[self.df["Livsmedelsnamn"].str.contains(ingredient, case=False)]

            # Remove courses
            filtered_data = filtered_data[~filtered_data["Gruppering"].str.contains("Rätter", case=False)]
            
            # Get choices (take Livsmedelsnamn and Gruppering and join with a ' | ')
            choices = filtered_data[["Livsmedelsnamn", "Gruppering"]].apply(lambda x: " | ".join(x), axis=1).tolist()

            # Check if the ingredient has been chosen before
            previous_choice = self.load_choice(ingredient)

            questions = [
                inquirer.List(
                    "ingredient_in_data",
                    message=f"Välj vilket livsmedel som motsvarar '{ingredient}'",
                    choices=choices,
                    default=previous_choice,
                ),
            ]

            answers = inquirer.prompt(questions)

            # Get index of answer
            index = choices.index(answers["ingredient_in_data"])

            # Get the row
            row = filtered_data.iloc[index]

            # Save the nutrition data as a row in the dataframe
            df_nutrition = pd.concat([df_nutrition, row.to_frame().T], axis=0, ignore_index=True)

            # Save the choice
            self.save_choice(ingredient, answers["ingredient_in_data"])

        return df_nutrition
        
    def save_choice(self, ingredient: str, choice: str):
        with open(self.choices_filename, "a") as f:
            f.write(f"{ingredient.lower()};{choice}\n")

    def load_choice(self, ingredient: str):
        if not os.path.exists(self.choices_filename): # If saved choices file does not exist, return None
            return None
        with open(self.choices_filename, "r") as f:
            for line in reversed(list(f)): # Read in reversed order to get the last choice
                if line.split(";")[0].lower() == ingredient.lower():
                    value = line.split(';')[1].strip()
                    print(f"Hittade tidigare val för ingridienten '{ingredient}': {value}", end="")
                    return value
        return None

class NutritionContent:
    def __init__(self, data: NutritionDataSource):
        self.data = data

        # Get available columns and filter out Livsmedelsnamn, Livsmedelsnummer and Gruppering
        self.columns = self.data.df.columns.tolist()
        self.columns = [column for column in self.columns if column not in ["Livsmedelsnamn", "Livsmedelsnummer", "Gruppering"]]

    def query_neutrition_content(self):

        content_dict = {column:None for column in self.columns}

        choices = ["✓ Klar", *self.columns, "✓ Klar"]
        index = None

        while True:
            questions = [
                inquirer.List(
                    "nutrient_to_specify",
                    message="Välj ett näringsämnen för att specificera hur mycket som finns i produkten",
                    choices=choices,
                    default=choices[index] if index is not None else None,
                ),
            ]

            answers = inquirer.prompt(questions)
            nutrient_to_specify = answers["nutrient_to_specify"]

            if nutrient_to_specify == "✓ Klar":
                # Check if all values are None. If it is, do not allow for finishing
                if all(value is None for value in content_dict.values()):
                    print("Du måste ange mängden för minst ett näringsämne.")
                    continue
                break

            # Get the index of the column
            index = choices.index(nutrient_to_specify)

            # Query how much of the nutrient is in the product
            questions = [
                inquirer.Text(
                    "nutrient_amount",
                    message=f"Ange hur mycket {nutrient_to_specify} som finns i produkten",
                ),
            ]

            answers = inquirer.prompt(questions)
            nutrient_amount = answers["nutrient_amount"]

            # If the answer is empty, set the value to None
            if nutrient_amount == "":
                nutrient_amount = None

            # If the answer is a number, convert it to a float. If not, then print warning and continue
            try:
                nutrient_amount = str(nutrient_amount).replace(",", ".").strip() # Replace comma with dot
                nutrient_amount = float(nutrient_amount)
            except ValueError:
                print(f"\nVarning: Du angav inte ett tal. Värdet för {nutrient_to_specify} har inte ändrats.")
                content_dict[nutrient_to_specify] = None
                continue

            # Add the nutrient to the dictionary
            content_dict[nutrient_to_specify] = nutrient_amount

            # Remove the nutrient from the choices
            choices.remove(nutrient_to_specify)

        return content_dict

# Minimization procedure to solve Ax = b
# Based on https://stackoverflow.com/a/31099263
def f(x, A, b):
    y = np.dot(A, x) - b
    return np.dot(y, y)

def solve_for_recipe(df_nutrition: pd.DataFrame, content_dict: dict):
    # Solve the system of equation Ax = b
    # A is the nutrition data for the ingredients
    # x is the amount of each ingredient
    # b is the nutrition content of the product

    # Filter out the values in the dict that are None
    content_dict = {key:value for key, value in content_dict.items() if value is not None}

    # Get the nutrition data for the ingredients
    A = df_nutrition[content_dict.keys()].to_numpy(dtype='float').T
    b = np.array(list(content_dict.values()), dtype='float')

    # Solve the system of equations
    # lstsq_res = np.linalg.lstsq(A, b, rcond=None) # Old method, could not have constraits and bounds

    # Solve the system of equations with constraints and bounds
    n_vars = A.shape[1]
    cons = ({'type': 'eq', 'fun': lambda x: x.sum() - 1})
    bounds = [(0, None)]*n_vars
    res = optimize.minimize(f, [0]*n_vars, method='SLSQP', constraints=cons, 
                        options={'disp': False}, bounds=bounds, args=(A, b))

    x = res['x']

    return x