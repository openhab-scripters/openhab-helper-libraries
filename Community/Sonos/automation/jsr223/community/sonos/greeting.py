'''
This script speaks a random greeting every minute on your Sonos speaker system.
To use this, you should set up astro.py as described here
https://github.com/OH-Jython-Scripters/lucid/blob/master/Script%20Examples/astro.py.
It also assumes that you've set up an openHAB contact items to represent the presence of
persons to be greeted. Each item should belong to the item group "G_Presence_Family".
'''
import random

from core.rules import rule
from core.triggers import when
from community.sonos.speak import tts, greeting
from configuration import PRIO
from core.utils import getItemValue

@rule("Greeting example")
@when("Time cron 0 * * * * ?")
def exampleGreeting(event):
    greetings = [greeting(), 'Hello', 'How are you', 'How are you doing', 'Good to see you', 'Long time no see', 'It\’s been a while']
    peopleAtHome = []
    for member in itemRegistry.getItem('G_Presence_Family').getAllMembers():
        if member.state == OPEN: peopleAtHome.append(member.label)
    random.shuffle(peopleAtHome)
    msg = random.choice(greetings)
    for i in range(len(peopleAtHome)):
        person = peopleAtHome[i]
        msg += ' '+person
        if i+2 == len(peopleAtHome):
            msg +=' and'
        elif i+1 == len(peopleAtHome):
            msg +='.'
        elif i+2 < len(peopleAtHome):
            msg +=','
    #tts(msg, PRIO['HIGH'], ttsRoom='Kitchen', ttsVol=42, ttsLang='en-GB', ttsVoice='Brian')
    tts(msg, PRIO['HIGH'], ttsRoom='Kitchen', ttsVol=42, ttsLang='en-IN', ttsVoice='Aditi')
    #tts(msg, PRIO['HIGH'], ttsRoom='Kitchen', ttsVol=42, ttsLang='en-US', ttsVoice='Matthew')
    #tts(msg, None, ttsRoom='All', ttsLang='de-DE', ttsVoice='Vicki')
    #tts(msg) # Also works if you accept the defaults