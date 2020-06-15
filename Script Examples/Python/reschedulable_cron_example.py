"""
This example provides a way to reschedule a cron rule based on the time portion
of a DateTimeItem. The cron rule ("Alarm clock" in the example) is removed and
recreated when the DateTimeItem's state is modified.
"""
from core.rules import rule
from core.triggers import when

@rule("Adjust rule trigger")
@when("Item Virtual_DateTime_1 changed")
@when("System started")
def adjust_rule_trigger(event):
    adjust_rule_trigger.log.warn("Cron Item changed")

    # if rule exists, remove it
    try:
        rule_uid = [rule_object for rule_object in rules.getAll() if rule_object.name == "Alarm clock"][0].UID
        adjust_rule_trigger.log.warn("Alarm clock rule exists, so removing it")
        scriptExtension.importPreset("RuleSupport")
        ruleRegistry.remove(rule_uid)
    except:
        pass

    # create rule
    time = items["Virtual_DateTime_1"].zonedDateTime
    @rule("Alarm clock")
    @when("Time cron {} {} {} * * ?".format(time.second, time.minute, time.hour))
    def alarm_clock(event):
        alarm_clock.log.warn("Wake up!")
