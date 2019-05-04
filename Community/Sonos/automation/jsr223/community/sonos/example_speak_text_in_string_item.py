from core.rules import rule
from core.triggers import when
from community.sonos.speak import tts

@rule("Example speak test in string Item", description="This script will speak the text located in the Speak_This Item when an update is received")
@when("Item Speak_This received update")
def exampleSpeakTextInStringItem(event):
    tts(event.ItemState)
