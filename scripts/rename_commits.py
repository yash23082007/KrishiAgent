import os

# Temporary file to store the commit sequence count (using absolute path)
count_file = r"c:\Users\yash6\OneDrive\Desktop\New folder (6)\scripts\commit_count.txt"

if not os.path.exists(count_file):
    with open(count_file, "w") as f:
        f.write("1")
    print("commit 1")
else:
    with open(count_file, "r") as f:
        count = int(f.read().strip())
    new_count = count + 1
    with open(count_file, "w") as f:
        f.write(str(new_count))
    print(f"commit {new_count}")
