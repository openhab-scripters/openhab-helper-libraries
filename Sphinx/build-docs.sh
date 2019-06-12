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
TEMP_LIB="lib/python"
AUTOMATION_JSR="automation/jsr223/python"
TEMP_JSR="jsr223/python/scripts"
COMMUNITY="community"

# remove old docs output
echo "Removing html output..."
rm -R "$OUTPUT_DIR"

# remove old links
echo "Removing import temp files and links..."
find "$IMPORTS_DIR/$TEMP_LIB" -type l -exec unlink {} \;
rm -R "$IMPORTS_DIR"

# create folders
echo "Creating import temp folders"
mkdir -p "$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY"
mkdir -p "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY"
touch "$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY/__init__.py"

# create Core symlinks
echo "Creating Core import temp files and links..."
ln -rs "$CORE_DIR/$AUTOMATION_LIB/core" "$IMPORTS_DIR/$TEMP_LIB/core"
#ln -rs "$CORE_DIR/$AUTOMATION_JSR/core" "$IMPORTS_DIR/$TEMP_JSR/core"
rsync -a "$CORE_DIR/$AUTOMATION_JSR/core/" "$IMPORTS_DIR/$TEMP_JSR/core/"

# iter all toplevel folders in Community/
echo "Creating Community import temp files and links..."
for DIRNAME in $(find "$COMMUNITY_DIR" -maxdepth 1 -type d 2>/dev/null); do
    if [ "$DIRNAME" != "$COMMUNITY_DIR/$COMMUNITY" ]; then
        if [ -d "$DIRNAME/$AUTOMATION_LIB" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" ]; then
                    ln -rs "$PACKAGE" "$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY/$(basename $PACKAGE)"
                    echo "  Found package '$(basename $PACKAGE)' in '$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY'"
                fi
            done
        fi
        
        if [ -d "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
                    #ln -rs "$PACKAGE" "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY/$(basename $PACKAGE)"
                    rsync -a "$PACKAGE/" "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY/$(basename $PACKAGE)/"
                    echo "  Found script folder '$(basename $PACKAGE)' in '$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY'"
                fi
            done
        fi
    fi
done

# put __init__.py files in every folder that has scripts to make them importable
echo "Creating '__init__.py' files for scripts..."
for DIRNAME in $(find "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY" -type d 2>/dev/null); do
    touch "$DIRNAME/__init__.py"
done

# link vscode_style to /.venv/lib/python3.7/site-packages/pygments/styles
ln -rs ./_styles/vscode.py ../.venv/lib/python3.7/site-packages/pygments/styles/vscode.py

# run Sphinx
echo
echo "Switching to Python virtual environment..."
source $SCRIPT_DIR/../.venv/bin/activate
echo "Running Sphinx Build..."
sphinx-build -a $SCRIPT_DIR/ $OUTPUT_DIR/
echo "Sphinx Build finished"

# remove import temps
echo "Removing import temp files and links..."
find "$IMPORTS_DIR/$TEMP_LIB" -type l -exec unlink {} \;
rm -R "$IMPORTS_DIR"
unlink ../.venv/lib/python3.7/site-packages/pygments/styles/vscode.py

echo
echo "Finished building documentation"
echo
exit 0