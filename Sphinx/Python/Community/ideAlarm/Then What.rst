==========
Then what?
==========

After Configuration
===================

You have successfully finished the initial configuration of ideAlarm and it's time to do some testing and customize things so that they work the way you want them to.
You can't see any errors originating from ideAlarm in the openHAB log, right?


Create a Simple Sitemap for Testing
===================================

Let's create a simple sitemap.
It will help you to test your ideAlarm system.
Below is an example using four zones.
Use it as a template and modify it so it works on your system.

.. code-block::

	sitemap ideAlarm label="ideAlarm Site Map" {
		Frame label="Open Sections" {
			Default item=Z1_Open_Sections
			Default item=Z2_Open_Sections
			Default item=Z3_Open_Sections
			Default item=Z4_Open_Sections
		}

		Frame label="Arming Modes" {
			Default item=Z1_Arming_Mode valuecolor=[0="black", 1="orange", 2="red"]
			Default item=Z2_Arming_Mode valuecolor=[0="black", 1="orange", 2="red"]
			Default item=Z3_Arming_Mode valuecolor=[0="black", 1="orange", 2="red"]
			Default item=Z4_Arming_Mode valuecolor=[0="black", 1="orange", 2="red"]
		}

		Frame label="Statuses" {
			Default item=Z1_Status valuecolor=[0="green", 1="red", 2="red", 3="red", 4="black"]
			Default item=Z2_Status valuecolor=[0="green", 1="red", 2="red", 3="red", 4="black"]
			Default item=Z3_Status valuecolor=[0="green", 1="red", 2="red", 3="red", 4="black"]
			Default item=Z4_Status valuecolor=[0="green", 1="red", 2="red", 3="red", 4="black"]
		}

		Frame label="Toggle switches" {
			Default item=Toggle_Z1_Armed_Away
			Default item=Toggle_Z1_Armed_Home
			Default item=Toggle_Z2_Armed_Away
			Default item=Toggle_Z2_Armed_Home
			Default item=Toggle_Z3_Armed_Away
			Default item=Toggle_Z3_Armed_Home
			Default item=Toggle_Z4_Armed_Away
			Default item=Toggle_Z4_Armed_Home
		}

		Frame label="Entry Timers" {
			Default item=Z1_Entry_Timer
			Default item=Z2_Entry_Timer
			Default item=Z3_Entry_Timer
			Default item=Z4_Entry_Timer
		}

		Frame label="Exit Timers" {
			Default item=Z1_Exit_Timer
			Default item=Z2_Exit_Timer
			Default item=Z3_Exit_Timer
			Default item=Z4_Exit_Timer
		}

		Frame label="Nag Timers" {
			Default item=Z1_Nag_Timer
			Default item=Z2_Nag_Timer
			Default item=Z3_Nag_Timer
			Default item=Z4_Nag_Timer
		}

		Frame label="Alert Max Timer" {
			Default item=Z1_Alert_Max_Timer
			Default item=Z2_Alert_Max_Timer
			Default item=Z3_Alert_Max_Timer
			Default item=Z4_Alert_Max_Timer
		}

		Frame label="Doors" {
			Default item=Door_I_Bathroom valuecolor=[CLOSED="green", OPEN="red"]
			Default item=Door_GardenShed valuecolor=[CLOSED="green", OPEN="red"]
		}
		Frame label="Windows" {
			Default item=Window_Bathroom_2 valuecolor=[CLOSED="green", OPEN="red"]
			Default item=Window_Room_1 valuecolor=[CLOSED="green", OPEN="red"]
		}
		Frame label="Locks" {
			Default item=Door_1_Lock valuecolor=[OPEN="green", CLOSED="red"]
			Default item=Door_2_Lock valuecolor=[OPEN="green", CLOSED="red"]
			Default item=Door_3_Lock valuecolor=[OPEN="green", CLOSED="red"]
		}
		Frame label="Sirenes" {
			Default item=Siren_Indoors
			Default item=Siren_Gardenshed
		}
	}

Now you can use the arming mode toggle buttons, e.g. ``Toggle_Z1_Armed_Away``, ``Toggle_Z1_Armed_Home`` to toggle between armed and disarmed.
Try to arm a zone and trip a sensor.
Watch the log.
When a zone is tripped, the entry timer starts.
Toggling the zone to disarm will prevent the sirens from turning on.
The same procedure works to reset the zone to normal after an alert situation.

Now you probably have your own ideas how you should arm and disarm your zones.
You might want to use physical switches to do that, presence detection or a timer.
It's all up to you.
Just make ordinary openHAB scripts that operates on the toggle buttons (``Toggle_Z1_Armed_Away``, ``Toggle_Z1_Armed_Home``).


Create Event Helpers in ``custom.py``
=====================================

Until now your newly created alarm system doesn't really do much.
You should set up the ideAlarm Event Helpers to respond to various alarm events.
That's where the fun part starts!
You might want to have spoken messages, SMS sent, other kind of notifications or lights turned on on certain ideAlarm events.
So go ahead and extend your ideAlarm Event Helpers.
