#!/usr/bin/python

from __future__ import print_function

import os
import sys

if sys.version_info[0] < 3:
    input = raw_input

def bad_exit(msg, code=1):
    print(msg)
    print()
    sys.exit(code)

def is_comment(str):
    return str.strip()[0] in {"#", ";"}

def load_prefs(file, SEP="="):
    try:
        with open(file, "rU") as f:
            propertyList = []                   # To maintain order
            propertyDict = {}                   # To hold the values

            for line in f:
                pos = line.find(SEP)            # Locate the separator

                # If this is a comment, just add it as is.
                if is_comment(line):
                    propertyList.append(line)

                # Otherwise, extract the config information.
                elif pos >= 0:
                    k = line[:pos]                              # Key
                    v = line[pos + len(SEP):]                   # Value
                    propertyDict[k.strip()] = v.rstrip("\n")    # Write this to the dictionary
                    propertyList.append(k)                      # Keep track of the position of this key

    except IOError:
        return None

    # We have everything we need to know now.
    return (propertyList, propertyDict, SEP)

def save_prefs(file, contents):
    with open(file, "wt") as f:

        # Make sense of our information.
        keysAndComments = contents[0]
        properties = contents[1]
        SEP = contents[2]

        # Look at our contents.
        for item in keysAndComments:

            # Write the comment if we're at a comment.
            if is_comment(item):
                f.write(item)

            # Otherwise, write the key/value combination.
            else:
                f.write(item + SEP + properties[item.strip()])

            # Can't forget the final newline.
            f.write("\n")

# Merges these two preferences together
# with priority given to other
def overwrite_prefs(target, other):
    if not target:
        return other

    for (key, val) in other[1].iteritems():
        if not is_comment(key) and key not in target[1]:
            target[0].append(key)
        target[1][key] = val
    return target

# To be treated as constants.
SETTINGS_DIR = ".metadata/.plugins/org.eclipse.core.runtime/.settings"
PREFS_FILE = "org.eclipse.ui.workbench.prefs"

# Leave if no arguments are passed.
if len(sys.argv) < 2:
    bad_exit("Usage: python {0} <workspace location>".format(sys.argv[0]))

# Get the destination path, and leave if this isn't a workspace directory.
destinationPath = os.path.join(sys.argv[1], SETTINGS_DIR)
if not os.path.isdir(destinationPath):
    bad_exit("Not an Eclipse workspace directory.")

# Keep track of the workspace directory now.
workspacePath = os.path.realpath(sys.argv[1])
print("Found workspace: {0}".format(workspacePath))

# Get all existing preference information.
preferences = load_prefs(os.path.join(destinationPath, PREFS_FILE))
new_preferences = load_prefs(PREFS_FILE)
conflicts = set()

# Check for conflicts.
if preferences:

    # Assumed conflicts
    conflicts = set(preferences[1]).intersection(set(new_preferences[1]))

    # Test our assumptions.
    for key in conflicts.copy():
        x = preferences[1][key]
        y = new_preferences[1][key]

        # It's only a conflict if there's going to be a change.
        if x != y:
            print("Key \"{0}\" will be modified.".format(key))
            print("Old: {0}".format(x))
            print("New: {0}".format(y))
            print()

        # Otherwise, disregard it.
        else:
            conflicts.remove(key)

overwrite = True
if conflicts:
    print("Number of conflicts found: {0}".format(len(conflicts)))
    yn = input("This is your only warning.  Do you want to continue (y/N)? ")
    overwrite = yn.lower() == "y"

if overwrite:
    overwrite_prefs(preferences, new_preferences)
    save_prefs(os.path.join(destinationPath, PREFS_FILE), preferences)
    print("The new prefrences have been saved.")
    print("To finish, import the following files into Eclipse")
    print("manually, wherever appropriate:")
    print()
    print("thepeoplescoder.epf")
    print("thepeoplescoder-java-codeStyle-formatter.xml")
else:
    print("Operation aborted.")

print()
