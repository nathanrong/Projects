import os

os.system('cls')

# Input variables
a = 6
b = 13
name = 'uneven'
extension = '.inp'
# Specify the path to the Downloads folder (change username)
downloads_path = r'C:\Users\YourUsername\Downloads\batfiles.txt'

## Important for File Use
# Convert end of line sequence from CRLF to LF
# Convert file extension to .sh
# give permission to execute using: chmod +x [file]

run = []
all_runs = []
x = 1
y = 1
actual_runs = 0

# Generate file names and insert 'sleep 3' and 'echo' after every 5th actual "cl" run
for x in range(1, a + 1):
    for y in range(1, b + 1):
        file_name = f"{name}{x}{y}"
        all_runs.append(f"runv7 . {file_name}name &")
        actual_runs += 1  # Count the actual run

        # After every 5 actual "cl" runs, insert 'sleep 3' and an 'echo' statement
        if actual_runs % 5 == 0:
            all_runs.append("sleep 3")
            all_runs.append(f"echo 'This number of runs has been completed: {actual_runs}'")

all_runs.append(f"echo '{actual_runs} runs have been made!'")

# Write the generated batch file lines to 'batfiles.txt' in Downloads
with open(downloads_path, 'w') as f:
    f.write("\n".join(all_runs))

print("This is the last file: " + all_runs[-1])
print("\n" + "Code has completed!")