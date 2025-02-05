import os

os.system('cls')

folder_directory = r'C:\Users\YourUsername\Downloads'
folder_name = 'TEST'
folder_path = folder_directory + '\\' + folder_name
os.chdir(folder_path)

folder_list = os.listdir(folder_path)

for file in folder_list:
    if file[-4] == '.':
        folder_list.remove(file)

for file in folder_list:
    file_path = folder_path + "\\" + file
    file_list = os.listdir(file_path)
    os.chdir(file_path)

    identifier = file_path.split("even")[1].split("name")[0]

    for file in file_list:
        file_name = file.split(".")[0]
        file_name = ''.join(i for i in file_name if not i.isdigit())
        extension = file.split(".")[1]
        new_name = file_name + identifier + '.' + extension
        rename = os.rename(file, new_name)


print("\n" + "Code has completed!")
