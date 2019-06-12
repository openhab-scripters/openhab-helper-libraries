#!/bin/bash

echo
echo "Building openHAB Helper Libraries documentation"
echo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

IMPORTS_DIR="$SCRIPT_DIR/imports"
OUTPUT_DIR="$SCRIPT_DIR/../docs"
CORE_DIR="$SCRIPT_DIR/../Core"
COMMUNITY_DIR="$SCRIPT_DIR/../Community"
AUTOMATION_LIB="automation/lib/python"
AUTOMATION_JSR="automation/jsr223/python"
COMMUNITY="community"

# remove old docs output
echo "Removing html output..."
rm -R "$OUTPUT_DIR"

# remove old links
echo "Removing import symlinks..."
find "$IMPORTS_DIR" -type l -exec unlink {} \;

# create folders
echo "Creating import folders"
mkdir -p "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY"
mkdir -p "$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY"
touch "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY/__init__.py"

# create Core symlinks
echo "Creating Core import symlinks..."
ln -rs "$CORE_DIR/$AUTOMATION_LIB/core" "$IMPORTS_DIR/$AUTOMATION_LIB/core"
ln -rs "$CORE_DIR/$AUTOMATION_JSR/core" "$IMPORTS_DIR/$AUTOMATION_JSR/core"

# iter all toplevel folders in Community/
echo "Creating Community import symlinks..."
for DIRNAME in $(find "$COMMUNITY_DIR" -maxdepth 1 -type d 2>/dev/null); do
    if [ "$DIRNAME" != "$COMMUNITY_DIR/$COMMUNITY" ]; then
        if [ -d "$DIRNAME/$AUTOMATION_LIB" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" ]; then
                    ln -rs "$PACKAGE" "$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY/$(basename $PACKAGE)"
                    echo "  Found package '$(basename $PACKAGE)' in '$IMPORTS_DIR/$AUTOMATION_LIB/$COMMUNITY'"
                fi
            done
        fi
        
        if [ -d "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
                    ln -rs "$PACKAGE" "$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY/$(basename $PACKAGE)"
                    echo "  Found script '$(basename $PACKAGE)' in '$IMPORTS_DIR/$AUTOMATION_JSR/$COMMUNITY'"
                fi
            done
        fi
    fi
done
echo

# run Sphinx
echo "Switching to Python virtual environment..."
source $SCRIPT_DIR/../.venv/bin/activate
echo "Running Sphinx Build..."
sphinx-build -a $SCRIPT_DIR/ $OUTPUT_DIR/

echo "Finishing building documentation"
echo
exit 0