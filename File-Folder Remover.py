import os
import shutil

os.system('cls')

folder_name = 'Results#2'
folder_directory = r'C:\Users\YourUsername\Downloads'

top_folder = folder_directory + '\\' + folder_name

destination_folder = r'C:\Users\YourUsername\Downloads\Filtered-NoSpace'

for folder in os.listdir(top_folder):
    
    source_folder = os.path.join(top_folder, folder)
    print(source_folder)

    # Move all files from source folder to destination folder
    for filename in os.listdir(source_folder):
        source_file = os.path.join(source_folder, filename)
        destination_file = os.path.join(destination_folder, filename)
        shutil.move(source_file, destination_file)

    shutil.rmtree(source_folder)
shutil.rmtree(top_folder)

print("\n" + "Code has been completed!")
