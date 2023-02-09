import sys
import os

COMPILED_NAME = '/Users/almogcohen/bin/writepromd'

files = []
for (i, arg) in enumerate(sys.argv):
    if (i == 0):
        continue
    files.append(arg)

# Create a folder in /tmp/ for the compiled files
folder = '/tmp/writepromd'
if not os.path.exists(folder):
    os.mkdir(folder)
else:
    os.system('rm -r ' + folder)
    os.mkdir(folder)

# Copy the files to the folder
for file in files:
    os.system('cp ' + file + ' ' + folder)

# Zip the folder
os.system('cd ' + folder + '; zip -r writepromd.zip *')

# Add the shebang
os.system('echo "#!/usr/bin/env python3" | cat - ' + folder + '/writepromd.zip > temp && mv temp ' + folder + '/writepromd.zip')

# Move the zip to the COMPILED_NAME
os.system('mv ' + folder + '/writepromd.zip ' + COMPILED_NAME)

os.chmod(COMPILED_NAME, 0o755)