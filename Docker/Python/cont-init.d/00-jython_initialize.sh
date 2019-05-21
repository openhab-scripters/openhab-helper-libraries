## Export Jython's required Java options
export EXTRA_JAVA_OPTS="${EXTRA_JAVA_OPTS} ${JYTHON_JAVA_OPTS}"

## Clears jython's compiled classes in automation dir in case container has changed
find ${APPDIR}/conf/automation/lib/python -name '*\$py.class' -delete

## Ensure we are running new rule engine addon - is there a better way?
MISC_LINE=$(grep '^[[:space:]]\?misc' ${APPDIR}/conf/services/addons.cfg)
if [ $? -eq 0 ]; then
  ## ensure we have ruleengine enabled
  if [[ ${MISC_LINE} == *"ruleengine"* ]]; then
    echo "New rule engine is already included in the addons.cfg"
  else 
    sed -i 's/misc\s\?=\s\?/misc = ruleengine,/' ${APPDIR}/conf/services/addons.cfg
  fi
else
  ## Just append last line
  echo "misc = ruleengine" >> ${APPDIR}/conf/services/addons.cfg
fi
  
