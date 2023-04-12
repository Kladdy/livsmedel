import pandas as pd
from pprint import pprint
import inquirer

# kwargs are passed to the reading of the file
class NutritionDataSource:
    def __init__(self, filepath: str, **kwargs):
        self.filepath = filepath

        # Load the data
        if filepath.endswith(".xlsx"):
            self.df = pd.read_excel(filepath, **kwargs)
        else:
            raise ValueError("'filepath' must end with .xlsx")
        
    def get_nutrition_data(self, ingridients: list):
        
        for ingredient in ingridients:
            # Filter the data
            filtered_data = self.df[self.df["Livsmedelsnamn"].str.contains(ingredient, case=False)]
            
            questions = [
                inquirer.List(
                    "ingredient_in_data",
                    message=f"Vilket livsmedel motsvarar '{ingredient}'?",
                    choices=filtered_data["Livsmedelsnamn"].tolist(),
                ),
            ]

            answers = inquirer.prompt(questions)
            pprint(answers)
            
            # Print the data
            # print(filtered_data)
        


