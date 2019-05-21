## From which base container as in https://hub.docker.com/r/openhab/openhab/#image-variants eg. 2.4.0.M6-armhf-debian
ARG OPENHAB_VERSION
FROM openhab/openhab:${OPENHAB_VERSION}

## Where will we install jython inside container
ARG JYTHON_HOME="/opt/jython"
ARG JYTHON_VERSION="2.7.0"

## To avoid the need to setup jython's opts by the user, we will modify EXTRA_JAVA_OPTS in init scripts ENV provided for convinience if you need to run it by hand
ENV \
  JYTHON_HOME="${JYTHON_HOME}" \
  JYTHON_JAVA_OPTS="-Xbootclasspath/a:${JYTHON_HOME}/jython.jar -Dpython.home=${JYTHON_HOME} -Dpython.path=${JYTHON_HOME}/Lib:${APPDIR}/conf/automation/lib/python"

## Install to /opt but allow writing $class files by giving every one permission to write, openhab user is created only after container has started
RUN \
  mkdir -p ${JYTHON_HOME} && \
  wget http://central.maven.org/maven2/org/python/jython-installer/${JYTHON_VERSION}/jython-installer-${JYTHON_VERSION}.jar -O /tmp/jython-installer.jar && \
  java -jar /tmp/jython-installer.jar -s -d ${JYTHON_HOME}/ -t standard -e demo doc src && \
  rm /tmp/jython-installer.jar && \
  chmod -R o+w ${JYTHON_HOME} 

## Init scripts run on each container startup
ADD cont-init.d/* /etc/cont-init.d/
