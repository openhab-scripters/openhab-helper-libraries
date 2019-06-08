********
Triggers
********


    The following is a list of available triggers. Any text in square brackets
    (``[]``) indicates it is optional, and any text in CAPITAL LETTERS should
    be replaced with a value specific to your use case.

``"Item ITEM_NAME changed [from STATE] [to STATE]"``
----------------------------------------------------

      | ``"Item ITEM_NAME received update [STATE]"``
      | ``"Item ITEM_NAME received command [COMMAND]"``

  ```python
  from core.rules import rule
  from core.triggers import when

  @rule("This is the name of a test rule", tags=["Tag 1", "Tag 2"])
  @when("Item Test_Switch_1 received command OFF")
  @when("Item Test_Switch_2 received update ON")
  @when("Item gMotion_Sensors changed to ON")
  @when("Member of gMotion_Sensors changed to OFF")
  @when("Descendent of gContact_Sensors changed to ON")# Similar to 'Member of', but will create a trigger for each non-group sibling Item (think group_item.allMembers())
  @when("Thing kodi:kodi:familyroom changed")# ThingStatusInfo (from <status> to <status>) cannot currently be used in triggers
  @when("Channel astro:sun:local:eclipse#event triggered START")
  @when("System started")# 'System shuts down' cannot currently be used as a trigger, and 'System started' needs to be updated to work with Automation API updates
  @when("Time cron 55 55 5 * * ?")
  def testFunction(event):
      if items["Test_Switch_1"] == OnOffType.ON:
          events.postUpdate("Test_String_1", "The test rule has been executed!")
  ```
