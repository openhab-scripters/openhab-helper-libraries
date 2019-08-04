"""
REST Based Metadata Editor - Utilities
"""

import sys
from click import echo, BadParameter
import requests as http
from urllib.parse import urlparse
import json

if sys.version_info[0] < 3: # Python 2.x
    str = basestring
else: # Python 3.x
    pass


def rest_get(host, path, query=""):
    try:
        resp = http.get("http://{host}/rest/{path}?{query}".format(host=host, path=path, query=query))
        return resp
        #if resp.status_code == http.codes.ok:
        #    return resp
        #else:
        #    echo("ERROR: GET 'http://{host}/rest/{path}' failed with response: {code} - {doc}".format(host=host, path=path, code=resp.status_code, doc=http.status_codes._codes[resp.status_code][0].replace("_", " ").capitalize()))
        #    return None
    except Exception as ex:
        echo("ERROR: GET 'http://{host}/rest/{path}' failed with error: {error}".format(host=host, path=path, error=str(ex).split(":")[-1:][0].strip("',)").strip()))
        return False

def rest_post(host, path, payload):
    try:
        resp = http.post("http://{host}/rest/{path}".format(host=host, path=path), data=str(payload), headers={"Accept": "application/json", "Content-Type": "text/plain"})
        return resp
        #if resp.status_code == http.codes.ok:
        #    return resp
        #else:
        #    echo("ERROR: GET 'http://{host}/rest/{path}' failed with response: {code} - {doc}".format(host=host, path=path, code=resp.status_code, doc=http.status_codes._codes[resp.status_code][0].replace("_", " ").capitalize()))
        #    return None
    except Exception as ex:
        echo("ERROR: POST 'http://{host}/rest/{path}' failed with error: {error}".format(host=host, path=path, error=str(ex).split(":")[-1:][0].strip("',)").strip()))
        return False

def rest_put(host, path, payload):
    try:
        resp = http.put("http://{host}/rest/{path}".format(host=host, path=path), data=json.dumps(payload), headers={"Accept": "application/json", "Content-Type": "application/json"})
        return resp
        #if resp.status_code == http.codes.ok:
        #    return resp
        #else:
        #    echo("ERROR: GET 'http://{host}/rest/{path}' failed with response: {code} - {doc}".format(host=host, path=path, code=resp.status_code, doc=http.status_codes._codes[resp.status_code][0].replace("_", " ").capitalize()))
        #    return None
    except Exception as ex:
        echo("ERROR: PUT 'http://{host}/rest/{path}' failed with error: {error}".format(host=host, path=path, error=str(ex).split(":")[-1:][0].strip("',)").strip()))
        return False

def rest_delete(host, path):
    try:
        resp = http.delete("http://{host}/rest/{path}".format(host=host, path=path))
        return resp
        #if resp.status_code == http.codes.ok:
        #    return resp
        #else:
        #    echo("ERROR: GET 'http://{host}/rest/{path}' failed with response: {code} - {doc}".format(host=host, path=path, code=resp.status_code, doc=http.status_codes._codes[resp.status_code][0].replace("_", " ").capitalize()))
        #    return None
    except Exception as ex:
        echo("ERROR: DELETE 'http://{host}/rest/{path}' failed with error: {error}".format(host=host, path=path, error=str(ex).split(":")[-1:][0].strip("',)").strip()))
        return False

def validate_hostname(ctz, param, value):
    """Validates openHAB hostname
    
    Use only as a Click option validator."""
    if "://" not in value: value = "http://{}".format(value)
    try:
        parts = urlparse(value)
        host = parts.netloc
        if parts.path:
            if "rest" in parts.path.lower().split("/") and parts.path.lower().strip("/")[-4:] == "rest":
                host += "/" + parts.path.strip("/")[:-4]
                host = host.strip("/")
            else:
                host += parts.path
    except:
        raise BadParameter("Hostname invalid, must be like 'hostname[:port]' or 'ip_address[:port]'")
    try:
        echo("Testing connection to openHAB...", nl=False)
        resp = http.get("http://{host}/rest/".format(host=host))
    except Exception as ex:
        echo("Failed")
        raise BadParameter("Error while trying to connect to openHAB host '{host}': {error}".format(host=host, error=str(ex).split(":")[-1:][0].strip("',)").strip()))
    if resp.status_code == http.codes.ok:
        echo("OK")
        return host
    else:
        echo("Failed")
        raise BadParameter("Error when connecting to '{host}': HTTP Response: {code} - {doc}".format(host=host, code=resp.status_code, doc=http.status_codes._codes[resp.status_code][0].replace("_", " ").capitalize()))

def validate_item(item_or_item_name, host, query=""):
    """Checks if item exists and fetches it if it does, returns ``None`` if
    item does not exist"""
    if isinstance(item_or_item_name, str):
        resp = rest_get(host, "items/{name}".format(name=item_or_item_name), query=query)
        if not resp:
            return None
        elif resp.status_code == http.codes.ok:
            return json.loads(resp.text)
        else:
            return None
    elif isinstance(item_or_item_name, dict):
        return item_or_item_name
    else:
        echo("WARNING: [{}] is not a string or item".format(item_or_item_name))
        return None

def update_item(item, host):
    if isinstance(item, dict):
        resp = rest_put(host, "items/{item_name}".format(item_name=item["name"]), item)
        if resp:
            # 200 means item created, should do a check?
            return True if resp.status_code == [200, 201] else False
        else:
            return False
    else:
        return False