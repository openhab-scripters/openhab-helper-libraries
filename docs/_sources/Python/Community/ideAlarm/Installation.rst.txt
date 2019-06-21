============
Installation
============

Prerequisites
=============

The following should be installed, configured, tested and working before continuing with installing ideAlarm:

* openHAB expire binding
* openHAB persistence has been set up and working.
  See the Item groups suggestions below.
* Create the following Item Groups

    Some Items need to be persisted for ideAlarm to work.
    It's convenient to set up persistence to certain Item groups.
    The naming of the first two groups below is just a suggestion.
    You may name them differently but for simplicity it might be a good idea to use the suggested names.
    The important thing is that Items belonging to the groups following gets persisted to restore your system after a restart.

    .. code-block::

        Group G_PersistOnChange // Persist on change and system start up
        Group G_PersistOnUpdate // Persist on change and system start up. For temp, humidity sensors etc.

        Group G_VirtualDevice      (G_PersistOnChange)
        Group G_Timer
        Group G_Alarm              (G_PersistOnChange)
        Group G_Alarm_Z1           (G_Alarm)
        Group G_Alarm_Z2           (G_Alarm)
        Group G_AlarmArmingMode    (G_Alarm)
        Group G_AlarmStatus        (G_Alarm)

* Create Items for each alarm zone you intend to use

    For each alarm zone that you wish to define, create the following Items in one of your existing ``.items`` files located in the ``$OPENHAB_CONF/items`` folder.
    You are advised to keep the naming convention suggested at least until everything is set up and works well.
    Your first zone's Items get Item names starting with 'Z1'.
    Prepend your second zone Items with 'Z2' etc.

    .. code-block::

        Number Z1_Arming_Mode          "Z1 Arming Mode: [MAP(en_armingmode.map):%s]"    <alarm>     (G_AlarmArmingMode)
        Number Z1_Status               "Z1 Status: [MAP(en_zonestatus.map):%s]"         <alarm>     (G_AlarmStatus)

        Switch Toggle_Z1_Armed_Away    "Toggle Z1 Armed Away"                           <switch>    (G_VirtualDevice)    {expire="1s,command=OFF"}
        Switch Toggle_Z1_Armed_Home    "Toggle Z1 Armed Home"                           <switch>    (G_VirtualDevice)    {expire="1s,command=OFF"}

        Number Z1_Open_Sections        "Z1 open sections [%.0f]"                        <door>      (G_VirtualDevice)

        Switch Z1_Entry_Timer          "Z1 entry timer [%s]"                            <time>      (G_Timer)            {expire="15s,command=OFF"}
        Switch Z1_Exit_Timer           "Z1 exit timer [%s]"                             <time>      (G_Timer)            {expire="2m,command=OFF"}
        Switch Z1_Nag_Timer            "Z1 nag timer [%s]"                              <time>      (G_Timer)            {expire="4m,command=OFF"}
        Switch Z1_Alert_Max_Timer      "Z1 alert maximum time [%s]"                     <time>      (G_Timer)            {expire="20s,command=OFF"}


Installation of the ideAlarm package
====================================

* Follow the instruction for how to :ref:`install or update a Community package <Getting Started/Installation:Community>`.
  Make sure you haven't skipped the step to install the mapping files.
* Edit the configuration dictionary ``idealarm_configuration`` that you've previously inserted into the openhab-helper-libraries configuration file.
  See :ref:`Python/Community/IdeAlarm/Configuration:IdeAlarm Configuration` for details.
  Before saving you might want to copy and paste the contents of your configuration file into the form on `PythonBuddy <https://pythonbuddy.com/>`_ to verify that the Python syntax is valid.
* Save and reload the openhab-helper-libraries configuration as described in :ref:`Python/Reference:Modifying and Reloading Modules`.
* Create a custom library script.

    * The custom library script defines what custom actions that will occurr in your system for some specific alarm system events.
      To help you create a custom library script, there are two example files.
      Choose between ``custom_template.py.example`` and ``custom_template_verbose.py.example``.
    * If you followed the instruction properly for how to :ref:`install or update a Community package <Getting Started/Installation:Community>`, the two example files will reside in your ``$OPENHAB_CONF/automation/lib/python/personal/idealarm/`` directory.
      Rename one of those files to ``custom.py``.
    * Edit the ``custom.py`` file to suit your needs.
      Start simple and optionally add complexity after you see that things are working well.
