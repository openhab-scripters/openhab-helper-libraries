#!/bin/bash

IMPORTS_DIR="./imports"
CORE_DIR="./../Core"
COMMUNITY_DIR="./../Community"
AUTOMATION_LIB="automation/lib/python"
AUTOMATION_JSR="automation/jsr223/python"
COMMUNITY="community"

# remove old links
find "$IMPORTS_DIR" -type l -exec unlink {} \;

# create folders
mkdir -p "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY"
mkdir -p "$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY"
touch "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY/__init__.py"

# create Core symlinks
ln -rs "$CORE_DIR/$AUTOMATION_LIB/core" "$IMPORTS_DIR/$AUTOMATION_LIB/core"
ln -rs "$CORE_DIR/$AUTOMATION_JSR/core" "$IMPORTS_DIR/$AUTOMATION_JSR/core"

# iter all toplevel folders in Community/
for DIRNAME in $(find "$COMMUNITY_DIR" -maxdepth 1 -type d); do
    if [ "$DIRNAME" != "$COMMUNITY_DIR/$COMMUNITY" ]; then
        if [ -d "$DIRNAME/$AUTOMATION_LIB" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" -maxdepth 1 -type d); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" ]; then
                    ln -rs "$PACKAGE" "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY/$(basename $PACKAGE)"
                    #echo "$PACKAGE", "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY/$(basename $PACKAGE)", $(basename $PACKAGE)
                fi
            done
        fi
        
        if [ -d "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" -maxdepth 1 -type d); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
                    ln -rs "$PACKAGE" "$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY/$(basename $PACKAGE)"
                    #echo "$PACKAGE", "$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY/$(basename $PACKAGE)", $(basename $PACKAGE)
                fi
            done
        fi
    fi
done

source ./../.venv/bin/activate
sphinx-build -a ./ ./../docs/