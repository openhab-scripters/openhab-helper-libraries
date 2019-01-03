'''
This scripts speaks a random greeting every minute on your Sonos speaker system.
Please see: https://github.com/OH-Jython-Scripters/lucid/blob/master/README.md
To use this, you should set up astro.py as described
here https://github.com/OH-Jython-Scripters/lucid/blob/master/Script%20Examples/astro.py
It also assumes that you've set up an openHAB a contact items to represent the presence of
persons to be greeted. Each item should belong to the item group "G_Presence_Family".
'''

#from core.rules import rule, addRule
#from core.triggers import CronTrigger
from community.sonos.speak import tts
from configuration import PRIO
from core.utils import getItemValue
import random

'''
@rule
class SayHello(object):
    def getEventTriggers(self):
        return [
            CronTrigger(EVERY_MINUTE), # Runs every minute
        ]

    def execute(self, modules, inputs):
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

addRule(SayHello())
'''
from core.rules import rule
from core.triggers import when

@rule("Greeting example")
@when("Time cron " + EVERY_MINUTE)
def exampleGreeting(event):
    def greeting():
        # To use this, you should set up astro.py as described
        # here https://github.com/OH-Jython-Scripters/lucid/blob/master/Script%20Examples/astro.py
        # It will take care of updating the item 'V_TimeOfDay' for you
        timeOfDay = getItemValue('V_TimeOfDay', TIMEOFDAY['DAY'])
        greeting = {
            0: 'Good night',
            1: 'Good morning',
            2: 'Good day',
            3: 'Good evening'
        }
        if timeOfDay in greeting:
            return greeting[timeOfDay]
        else:
            return 'good day'
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