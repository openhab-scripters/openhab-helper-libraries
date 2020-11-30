"""
The ``flite_tts`` package provides the ``convert`` function that converts text
to speech.
"""
__all__ = ['tts_converter']

import re

from java.lang import System
from java.io import File

from core.log import logging, LOG_PREFIX, log_traceback
from core.actions import Exec
#import configuration
#reload(configuration)
from configuration import FLITE_TTS_CONFIGURATION, HOST_PORT_CONFIGURATION

LOG = logging.getLogger("{}.flite_tts".format(LOG_PREFIX))

@log_traceback
def tts_converter(content):
    LOG.debug(u"start:\n{}".format(content).decode('utf-8'))
    
    # Get the file object for the appropriate prefix sound and if the content
    # always changes, then don't save the file (recycle it)
    openhab_conf = System.getenv("OPENHAB_CONF")
    alert_prefix = File.separator.join([openhab_conf, "html", "TTS", "Alert_Prefix.mp3"])
    recycled = False
    if "Weather Alert:" in content:
        alert_prefix = File.separator.join([openhab_conf, "html", "TTS", "Alert_Weather.mp3"])
        recycled = True
    elif any(alert_type in content for alert_type in FLITE_TTS_CONFIGURATION["recycle"]):
        recycled = True
    file_name = "recycled.wav"
    if not recycled:
        # Since the file is being saved, truncate the filename to 150 allowed characters
        file_name = re.sub("[^a-zA-Z0-9_.-]", "", content)
        if len(file_name) > 149:
            file_name = file_name[0:149]
        file_name = "{}.wav".format(file_name)
    
    # Substitute text to help TTS pronounce some words
    content_scrubbed = content
    for key, value in FLITE_TTS_CONFIGURATION["substitutions"].items():
        content_scrubbed = content_scrubbed.replace(key, value)
    
    # Set paths and files, creating them if they do not exist
    voice = File(FLITE_TTS_CONFIGURATION["path_to_voice"]).getName()
    directory_path_name = File.separator.join([openhab_conf, "html", "TTS", voice])
    directory_path = File(directory_path_name)
    if not directory_path.exists():
        directory_path.mkdir()
    file_path_name = File.separator.join([directory_path_name, file_name])
    file_path = File(file_path_name.replace(".wav", ".mp3"))
    
    # If it does not yet exist, generate the TTS
    if recycled or not file_path.exists():
        Exec.executeCommandLine(u"{}@@-voice@@{}@@-t@@{}@@-o@@{}".format(FLITE_TTS_CONFIGURATION["path_to_flite"], FLITE_TTS_CONFIGURATION["path_to_voice"], content_scrubbed, file_path_name), 60000)
        Exec.executeCommandLine(u"{}@@-y@@-i@@{}@@-af@@volume=10, highpass=f=500, lowpass=f=3000@@{}".format(FLITE_TTS_CONFIGURATION["path_to_ffmpeg"], file_path_name, file_path_name.replace(".wav", ".mp3")), 60000)
        Exec.executeCommandLine(u"{} -y -i \"concat:{}|{}\" -c copy {}".format(FLITE_TTS_CONFIGURATION["path_to_ffmpeg"], alert_prefix, file_path_name.replace(".wav", ".mp3"), file_path_name.replace(".wav", ".combined.mp3")), 60000)
    
    # Create the URL used in the PlayURI
    result = "http://{}:{}/static/TTS/{}/{}".format(HOST_PORT_CONFIGURATION.get("openhab").get("host"), HOST_PORT_CONFIGURATION.get("openhab").get("port"), voice, file_name.replace(".wav", ".combined.mp3"))
    LOG.debug(u"complete:\n{}".format(content).decode('utf-8'))
    return result
