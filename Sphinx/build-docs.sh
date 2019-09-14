#!/bin/bash

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

echo
echo "Building openHAB Helper Libraries documentation"
echo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

IMPORTS_DIR="$SCRIPT_DIR/imports"
OUTPUT_DIR="$SCRIPT_DIR/../docs"
CORE_DIR="$SCRIPT_DIR/../Core"
COMMUNITY_DIR="$SCRIPT_DIR/../Community"
EXAMPLES_DIR="$SCRIPT_DIR/../Script Examples/Python"
#DESIGN_PATTERNS_DIR="$SCRIPT_DIR/../Design Patterns"

AUTOMATION_LIB="automation/lib/python"
TEMP_LIB="lib/python"
AUTOMATION_JSR="automation/jsr223/python"
TEMP_JSR="jsr223/python/scripts"

PERSONAL="personal"
COMMUNITY="community"
CORE="core"
EXAMPLES="examples"

# remove old docs output
if [[ -d $OUTPUT_DIR ]]; then
    echo "Removing previous '/docs/' directory [$OUTPUT_DIR]..."
    rm -R "$OUTPUT_DIR"
fi

# remove old import directory
if [[ -d $IMPORTS_DIR ]]; then
    echo "Removing previous temp '/import/' directory [$IMPORTS_DIR]..."
    rm -R "$IMPORTS_DIR" 2>/dev/null
fi

# create folders
echo "Creating temp '/import/' directory structure..."
mkdir -p "$IMPORTS_DIR/$TEMP_LIB/$CORE"
mkdir -p "$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY"
mkdir -p "$IMPORTS_DIR/$TEMP_JSR/$CORE"
mkdir -p "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY"
mkdir -p "$IMPORTS_DIR/$TEMP_JSR/$EXAMPLES"

# Copy /Core/
echo "Copying '/Core/' directories to temp '/import/' directory..."
rsync -a --protect-args "$CORE_DIR/$AUTOMATION_LIB/" "$IMPORTS_DIR/$TEMP_LIB"
rsync -a --protect-args "$CORE_DIR/$AUTOMATION_JSR/" "$IMPORTS_DIR/$TEMP_JSR"

# Copy /Script Examples/
echo "Copying '/Script Examples/ directories to temp '/import/' directory..."
rsync -a --protect-args "$EXAMPLES_DIR/" "$IMPORTS_DIR/$TEMP_JSR/$EXAMPLES"

# Iterate all toplevel folders in /Design Patterns/
#echo "Copying '/Design Patterns/' directories to temp '/import/' directory..."
#for DIRNAME in $(find "$DESIGN_PATTERNS_DIR" -maxdepth 1 -type d 2>/dev/null); do
#    #echo $DIRNAME
#    if [ "$DIRNAME" != "$DESIGN_PATTERNS_DIR" ]; then
#        if [ -d "$DIRNAME/$AUTOMATION_JSR/personal" ]; then
#            for MODULE in $(find "$DIRNAME/$AUTOMATION_JSR/personal" -maxdepth 1 -type f 2>/dev/null); do
#                rsync -a --protect-args "$MODULE" "$IMPORTS_DIR/$TEMP_JSR/$EXAMPLES/$(basename $MODULE)"
#                echo "  Found design pattern folder '$(basename $MODULE)' in '$DIRNAME/$AUTOMATION_JSR/personal'"
#            done
#        fi
#    fi
#done

# Iterate all toplevel folders in /Community/
echo "Copying '/Community/' directories to temp '/import/' directory..."
for DIRNAME in $(find "$COMMUNITY_DIR" -maxdepth 1 -type d 2>/dev/null); do
    #echo $DIRNAME
    if [ "$DIRNAME" != "$COMMUNITY_DIR" ]; then
        if [ -d "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_LIB/$COMMUNITY" ]; then
                    rsync -a --protect-args "$PACKAGE/" "$IMPORTS_DIR/$TEMP_LIB/$COMMUNITY/$(basename $PACKAGE)/"
                    #echo "  Found package '$(basename $PACKAGE)' in '$DIRNAME/$AUTOMATION_LIB/$COMMUNITY'"
                    #echo "     Found package '$(basename $PACKAGE)' in '/$AUTOMATION_LIB/$COMMUNITY'"
                    echo "     Found package '/$AUTOMATION_LIB/$COMMUNITY/$(basename $PACKAGE)'"
                fi
            done
        fi

        if [ -d "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_JSR/$COMMUNITY" ]; then
                    rsync -a --protect-args "$PACKAGE/" "$IMPORTS_DIR/$TEMP_JSR/$COMMUNITY/$(basename $PACKAGE)/"
                    #echo "  Found script folder '$(basename $PACKAGE)' in '$DIRNAME/$AUTOMATION_JSR/$COMMUNITY'"
                    echo "     Found script folder '/$AUTOMATION_JSR/$COMMUNITY/$(basename $PACKAGE)'"
                fi
            done
        fi

        if [ -d "$DIRNAME/$AUTOMATION_LIB/$PERSONAL" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_LIB/$PERSONAL" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_LIB/$PERSONAL" ]; then
                    rsync -a --protect-args "$PACKAGE/" "$IMPORTS_DIR/$TEMP_LIB/$PERSONAL/$(basename $PACKAGE)/"
                    #echo "  Found package '$(basename $PACKAGE)' in '$DIRNAME/$AUTOMATION_LIB/$COMMUNITY'"
                    echo "     Found package '/$AUTOMATION_LIB/$PERSONAL/$(basename $PACKAGE)'"
                fi
            done
        fi

        if [ -d "$DIRNAME/$AUTOMATION_JSR/$PERSONAL" ]; then
            for PACKAGE in $(find "$DIRNAME/$AUTOMATION_JSR/$PERSONAL" -maxdepth 1 -type d 2>/dev/null); do
                if [ "$PACKAGE" != "$DIRNAME/$AUTOMATION_JSR/$PERSONAL" ]; then
                    rsync -a --protect-args "$PACKAGE/" "$IMPORTS_DIR/$TEMP_JSR/$PERSONAL/$(basename $PACKAGE)/"
                    #echo "  Found script folder '$(basename $PACKAGE)' in '$DIRNAME/$AUTOMATION_JSR/$PERSONAL'"
                    echo "     Found script folder '/$AUTOMATION_JSR/$PERSONAL/$(basename $PACKAGE)'"
                fi
            done
        fi
    fi
done

# Generate a configuration module
#echo "Generating configuration module..."
#touch $IMPORTS_DIR/$TEMP_LIB/configuration.py
#for FILENAME in $(find "$COMMUNITY_DIR" -type f 2>/dev/null); do
#    if [[ $FILENAME =~ "configuration.py.example" ]]; then
#        cat $FILENAME >> $IMPORTS_DIR/$TEMP_LIB/configuration.py
#        echo "  Added $FILENAME into configuration.py"
#    fi
#done
#for FILENAME in $(find "$CORE_DIR" -type f 2>/dev/null); do
#    if [[ $FILENAME =~ "configuration.py.example" ]]; then
#        cat $FILENAME >> $IMPORTS_DIR/$TEMP_LIB/configuration.py
#        echo "  Added $FILENAME into configuration.py"
#    fi
#done

# Rename any .examples
echo "Renaming '.example' modules and scripts..."
#for FILENAME in $(find "$IMPORTS_DIR/$TEMP_LIB" -type f 2>/dev/null); do
#    if [[ $FILENAME =~ "py.example" ]]; then
#        NEW_NAME=${FILENAME/\.example/}
#        mv $FILENAME $NEW_NAME
#        #echo "  Renamed $FILENAME to $NEW_NAME"
#        echo "     Renamed '$FILENAME' to '$(basename $NEW_NAME)'"
#    fi
#done

for FILENAME in $(find "$IMPORTS_DIR/$TEMP_JSR" -type f 2>/dev/null); do
    if [[ $FILENAME =~ "py.example" ]]; then
        NEW_NAME=${FILENAME/\.example/}
        mv $FILENAME $NEW_NAME
        #echo "  Renamed $FILENAME to $NEW_NAME"
        echo "     Renamed '${FILENAME/$IMPORTS_DIR/}' to '$(basename $NEW_NAME)'"
    fi
done

# Adding imports for things used in default scope for all scripts
echo "Replacing default scope symbols and others in scripts with mocks..."
for FILENAME in $(find "$IMPORTS_DIR/$TEMP_JSR" -type f 2>/dev/null); do
    sed -i -e 's/^scriptExtension.importPreset/import Visibility\nimport TriggerHandlerFactory\nimport ActionHandler\nimport ActionType\nimport ConfigDescriptionParameter\nimport ConfigDescriptionParameterBuilder\nimport automationManager\nimport scriptExtension\nscriptExtension.importPreset/' $FILENAME
    sed -i -e 's/^if not itemRegistry.getItem/import itemRegistry\nif not itemRegistry.getItem/' $FILENAME
    sed -i -e 's/^reload/import reload\nreload/' $FILENAME
done

# Replacing imports of core modules with mocks
echo "Replacing imports of core modules with mocks..."
for FILENAME in $(find "$IMPORTS_DIR" -type f 2>/dev/null); do
    if [[ ${FILENAME: -3} == ".py" ]]; then
        #echo $FILENAME
        sed -i -e 's/from core/from core_mock/' $FILENAME
        #echo "     Replaced core imports with mocks for '$(basename $FILENAME)'"
    fi
done

# Clear everything but the docstrings in files with errors that cannot be resolved
echo "Clearing contents of scripts with errors that cannot be resolved..."
for FILENAME in $(find "$IMPORTS_DIR" -type f 2>/dev/null); do
    if [[ $FILENAME =~ "000_startup_delay" ]]; then #|| $FILENAME =~ "rule_registry_example" ]]; then
        sed -n -i -e '/"""/,/"""/p' $FILENAME
        #sed -i '/^$/q' $FILENAME
        echo "     Removed everything but the docstring from '$(basename $FILENAME)'"
    fi
done

# Add __init__.py files to all directries containing core and community scripts to make them importable
echo "Creating '__init__.py' files for core and community scripts..."
for DIRNAME in $(find "$IMPORTS_DIR/$TEMP_JSR" -type d 2>/dev/null); do
    touch "$DIRNAME/__init__.py"
done

# Add __init__.py files to all directries containing script examples to make them importable
echo "Creating '__init__.py' files for script examples..."
for DIRNAME in $(find "$IMPORTS_DIR/$TEMP_EXAMPLES/Python" -type d 2>/dev/null); do
    touch "$DIRNAME/__init__.py"
done

# link vscode_style to /.venv/lib/python3.7/site-packages/pygments/styles
STYLE_LINK="$(find "$SCRIPT_DIR/../.venv/lib" -type d -name "pygments")/styles/vscode.py"
#STYLE_LINK="/usr/lib/python2.7/site-packages/pygments/styles/vscode.py"
ln -rs "$SCRIPT_DIR/_styles/vscode.py" "$STYLE_LINK"

# run Sphinx
echo
echo "Switching to Python virtual environment..."
source $SCRIPT_DIR/../.venv/bin/activate
echo "Running Sphinx Build..."
sphinx-build -a $SCRIPT_DIR/ $OUTPUT_DIR/
echo "Sphinx Build finished"

# remove import temps
echo "Removing import temp files and links..."
rm -R "$IMPORTS_DIR"
unlink "$STYLE_LINK"

IFS=$SAVEIFS

echo
echo "Finished building documentation"
echo
exit 0

#: <<'end_comment'
#end_comment
