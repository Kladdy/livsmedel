import datetime

title_string = """
 _     _                              _      _ 
| |   (_)                            | |    | |
| |    ___   _____ _ __ ___   ___  __| | ___| |
| |   | \ \ / / __| '_ ` _ \ / _ \/ _` |/ _ \ |
| |___| |\ V /\__ \ | | | | |  __/ (_| |  __/ |
\_____/_| \_/ |___/_| |_| |_|\___|\__,_|\___|_|
"""

author = "Sigfrid Stjärnholm"
year = datetime.datetime.now().year

def print_title():
    print(title_string)
    # Print author and year, right adjusted
    print(f"© {author} ({year})".rjust(len(title_string.splitlines()[1])))
    print("")