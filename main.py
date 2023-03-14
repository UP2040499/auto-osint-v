"""
This module forms the main part of the program, where other modules are run from.
"""

import os
import webbrowser
import csv

def input_intelligence():
    """
    This method creates a text file for the user to input their intelligence statement into.
    """
    print("Intelligence statement help:\n")
    print("- Please include as much information as possible\n")
    print("- If an entity is a person please include known associates:")
    print("A notepad window will now open - enter the intelligence statement in there.")
    data_path = os.getcwd() + "/DataFiles/"
    intelligence_filepath = str(os.path.join(data_path,"intelligence_file.txt"))
    if os.path.isfile(intelligence_filepath):
        os.remove(intelligence_filepath)
    with open(intelligence_filepath, "x", encoding="utf-8") as fout:
        # Create file and close as will be edited in txt editor.
        fout.close()
        webbrowser.open(intelligence_filepath) # edit in chosen text editor

def input_bias_sources():
    """
    This function will create a csv file for the bias sources to be stored in.
    """
    print("Enter a Bias Source")
    print("You will now be asked to enter any sources you believe are important to compare to.")
    print("This allows other sources of intelligence \
          (such as closed or classified sources) to be compared.")
    option = str(input("Press ENTER to continue or press 'X' to skip this step. >>> "))
    if option in {"x", "X"}:
        return

    data_path = os.getcwd() + "/DataFiles/"
    bias_filepath = str(os.path.join(data_path, "bias_sources.csv"))
    with open(bias_filepath,"w", encoding="utf-8") as bfile:
        fieldnames = ['Type', 'Key_Info']
        writer = csv.DictWriter(bfile, fieldnames)
        # enter source type and key information
        writer.writeheader()
        while option not in {"x", "X"}:
            source_type = str(input("Enter the source/intelligence type, \
                                    for example HUMINT, SIGINT, etc.\n>>> "))
            key_info = str(input("Enter the key information proffered \
                                 from this source/intelligence\n>>> "))
            writer.writerow({"Type": source_type, "Key_Info": key_info})
            option = str(input("Enter 'X' to finish entering sources. \
                               Press ENTER to add another source>>> "))
        bfile.close()

if __name__ == '__main__':
    # This code won't run if this file is imported.
    input_intelligence()
    input_bias_sources()
