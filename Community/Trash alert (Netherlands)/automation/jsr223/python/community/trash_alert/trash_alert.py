"""
This script contains a rule that consults afvalkalenders for garbage pickup
times twice a day and update Items with the dates. The script can create the
Items needed, if they do not exist.

Please configure this script by filling in your address data in
afvalkalender_configuration below. Please select the base URI for your garbage
collector provider from the list below:

MijnAfvalWijzer: https://json.mijnafvalwijzer.nl
Cyclus NV: https://afvalkalender.cyclusnv.nl
HVC: https://apps.hvcgroep.nl
Dar: https://afvalkalender.dar.nl
Afvalvrij / Circulus-Berkel: https://afvalkalender.circulus-berkel.nl
Meerlanden: https://afvalkalender.meerlanden.nl
Cure: https://afvalkalender.cure-afvalbeheer.nl
Avalex: https://www.avalex.nl
RMN: https://inzamelschema.rmn.nl
Venray: https://afvalkalender.venray.nl
Den Haag: https://huisvuilkalender.denhaag.nl
Berkelland: https://afvalkalender.gemeenteberkelland.nl
Alphen aan den Rijn: https://afvalkalender.alphenaandenrijn.nl
Waalre: https://afvalkalender.waalre.nl
ZRD: https://afvalkalender.zrd.nl
Spaarnelanden: https://afvalwijzer.spaarnelanden.nl
Montfoort: https://afvalkalender.montfoort.nl
GAD: https://inzamelkalender.gad.nl
Cranendonck: https://afvalkalender.cranendonck.nl

List taken from: https://www.gadget-freakz.com/domoticz-dzvents-getgarbagedates-script/
"""
import json
from datetime import datetime, timedelta

from core.rules import rule
from core.triggers import when
from core.items import add_item
from core.actions import HTTP
from core.utils import postUpdate as post_update
# personal library used to push a notification to your preferred messaging system (e.g. myopenhab or telegram)
from personal.utils import notification

afvalkalender_configuration = {
    'huisnummer': "5",
    'toevoeging': '',
    'postcode': "1234AB",
    'afvalkalender_url': '',
    # 'huisnummer': "17",
    # 'toevoeging': '',
    # 'postcode': "5581BG",
    # 'afvalkalender_uri': 'https://afvalkalender.waalre.nl',
    'create_missing_items': False
}

@rule("Trash pickup dates", description="Haal de gegevens over ophalen van afval op uit de afvalwijzer", tags=["afvalkalender"])
@when("Time cron 0 30 7 * * ?")
@when("Time cron 0 30 19 * * ?")
def send_trash_pickup_notifications(event):
    # Get data from mijnafvalwijzer
    postcode = afvalkalender_configuration['postcode']
    huisnummer = afvalkalender_configuration['huisnummer']
    toevoeging = afvalkalender_configuration['toevoeging']
    send_trash_pickup_notifications.log.debug('Getting pickup dates for {}-{}{}'.format(postcode, huisnummer, toevoeging))
    if 'afvalkalender_uri' in afvalkalender_configuration and afvalkalender_configuration['afvalkalender_uri'] and afvalkalender_configuration['afvalkalender_uri'] != 'https://json.mijnafvalwijzer.nl':
        pickupdates = get_pickupdates_afvalkalender(postcode, huisnummer, afvalkalender_configuration['afvalkalender_uri'])
    else:
        pickupdates = get_pickupdates_mijnafvalwijzer(postcode, huisnummer, toevoeging)

    process_pickupdates(pickupdates, 'papier', 'oud papier', 'AfvalKalender_papier')
    process_pickupdates(pickupdates, 'gft', 'groente-, fruit- en tuinafval', 'AfvalKalender_gft')
    process_pickupdates(pickupdates, 'restafval', 'restafval', 'AfvalKalender_restafval')
    process_pickupdates(pickupdates, 'pmd', 'plastic- en metaalafval en drinkkartons', 'AfvalKalender_pmd')
    process_pickupdates(pickupdates, 'kca', 'klein chemisch afval', 'AfvalKalender_kca')

def process_pickupdates(dates, type, description, item, now=None):
    if not dates or len(dates) == 0:
        return
    pickup_dates = [x['date'] for x in dates if x['type'] == type]
    if pickup_dates.empty():
        return
    if now is None:
        now = datetime.now()
    send_trash_pickup_notifications.log.debug(u"Processing pickup dates for {}: {} and item {} on {}".format(type, description, item, now))
    if itemRegistry.getItems(item) == []:
        if afvalkalender_configuration['create_missing_items']:
            add_item(item, item_type="DateTime", label="{} [%%1$td-%1$tm]".format(description), category="Calendar", groups=[], tags=[])
        else:
            return
    today = str(now.date())
    tomorrow = str(now.date() + timedelta(days=1))
    next_date = next((d for d in pickup_dates if d >= today), pickup_dates[-1])
    next_date_list = next_date.split("-")
    pickup_date = DateTimeType().zonedDateTime.withYear(int(next_date_list[0])).withMonth(int(next_date_list[1])).withDayOfMonth(int(next_date_list[2])).withHour(0).withMinute(0).withSecond(0).withNano(0)
    post_update(item, str(pickup_date))
    current_time = now.time()
    if today == next_date and current_time.hour <= 12:
        message = u"Vandaag wordt het {} opgehaald.".format(description)
        send_trash_pickup_notifications.log.info(message)
        notification(message)
    if tomorrow == next_date and current_time.hour > 12:
        message = u"Morgen wordt het {} opgehaald.".format(description)
        send_trash_pickup_notifications.log.info(message)
        notification(message)

def get_json_response(URI):
    the_page = HTTP.sendHttpGetRequest(URI, 5000)
    if not the_page:
        send_trash_pickup_notifications.log.warn("Could not get response from {}".format(URI))
        return
    try:
        return json.loads(the_page.decode('utf-8'))
    except Exception as ex:
        send_trash_pickup_notifications.log.warn(u"Could not interpret json response from {}: {}".format(URI, ex))

def get_pickupdates_mijnafvalwijzer(postcode, huisnummer, toevoeging=''):
    """
    This function gets the pickup dates from different garbage collectors from
    mijnafvalwijzer.
    """
    URI = 'https://json.mijnafvalwijzer.nl/?method=postcodecheck&postcode={0}&huisnummer={1}&toevoeging={2}'.format(postcode, huisnummer, toevoeging)
    pickupdates = {}
    try:
        response = get_json_response(URI)
        pickupdates = response['data']['ophaaldagen']
        if pickupdates[u'response'] != u'OK':
            send_trash_pickup_notifications.log.warn(u"Invalid response while getting garbage pickup dates from {}: {}".format(URI, pickupdates['error']))
            return
        else:
            return pickupdates['data']
    except Exception as ex:
        send_trash_pickup_notifications.log.warn(u"Could not interpret garbage pickup dates from {}: {}".format(URI, ex))
        return

"""
Gets pickup dates from different garbage collectors. Please select the base URI for
your garbage collector from the list below

Cyclus NV: https://afvalkalender.cyclusnv.nl
HVC: https://apps.hvcgroep.nl
Dar: https://afvalkalender.dar.nl
Afvalvrij / Circulus-Berkel: https://afvalkalender.circulus-berkel.nl
Meerlanden: https://afvalkalender.meerlanden.nl
Cure: https://afvalkalender.cure-afvalbeheer.nl
Avalex: https://www.avalex.nl
RMN: https://inzamelschema.rmn.nl
Venray: https://afvalkalender.venray.nl
Den Haag: https://huisvuilkalender.denhaag.nl
Berkelland: https://afvalkalender.gemeenteberkelland.nl
Alphen aan den Rijn: https://afvalkalender.alphenaandenrijn.nl
Waalre: https://afvalkalender.waalre.nl
ZRD: https://afvalkalender.zrd.nl
Spaarnelanden: https://afvalwijzer.spaarnelanden.nl
Montfoort: https://afvalkalender.montfoort.nl
GAD: https://inzamelkalender.gad.nl
Cranendonck: https://afvalkalender.cranendonck.nl

List taken from: https://www.gadget-freakz.com/domoticz-dzvents-getgarbagedates-script/
"""
def get_pickupdates_afvalkalender(postcode, huisnummer, afvalkalender_URI):
    URI1=u"{0}/rest/adressen/{1}-{2}".format(afvalkalender_URI, postcode, huisnummer)
    response1 = get_json_response(URI1)
    if not response1:
        send_trash_pickup_notifications.log.warn(u"Could not get garbage pickup information from {}".format(URI1))
        return
    URI2=u"{0}/rest/adressen/{1}/afvalstromen".format(afvalkalender_URI, response1[0]['bagId'])
    response2 = get_json_response(URI2)
    if not response2:
        send_trash_pickup_notifications.log.warn(u"Could not get garbage pickup dates from {}".format(URI2))
        return
    pickupdates = []
    for pd in response2:
        newdate = {}
        if pd['icon'] and pd['ophaaldatum']:
            newdate['type'] = pd['icon']
            newdate['date'] = pd['ophaaldatum']
            if newdate['type'] == 'rest':
                newdate['type'] = 'restafval'
            pickupdates.append(newdate)
 
    return pickupdates
