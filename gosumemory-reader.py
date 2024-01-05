# This is an OBS script pulled out from the author. For inspecting stuff.

#i hate people who codes without commenting with a passion.

import obspython as obs
import websocket as websockets
import json
import threading
import time
import traceback

api_endpoint = ""
jsonpath = ""
text_source = ""

format_rule = ""
format_args = []
cached_json = ""

websocket_thread = None
old_text = ""

thread_ws_stop = False
new_state = {}

DEBUG = False

# ------------------------------------------------------------
# Script by @KotRikD
# Written in 2020 for gosumemory
# ------------------------------------------------------------

def on_message(ws, message):
    if thread_ws_stop:
        ws.close()
    global jsonpath
    global format_args

    try:
        jsoned_message = json.loads(message)

        # probably needs a better way of doing this
        if type(jsonpath) == str:
            lol = eval('jsoned_message["'+jsonpath.replace(".", '"]["')+'"]')
            format_args[0] = str(lol)
        elif type(jsonpath) in [list, tuple]:
            for (ind, key) in enumerate(jsonpath):
                value = eval('jsoned_message["'+key.replace(".", '"]["')+'"]')
                format_args[ind] = value

        update_text(format_rule.format(*format_args))
    except Exception:
        traceback.print_exc()


def on_any_trouble(ws, error=None):
    if DEBUG:
        obs.script_log(
            obs.LOG_WARNING, f"Oops, looks like ws is crashed by N-reason: {error}")


def run_ws():
    global api_endpoint

    if DEBUG:
        obs.script_log(
            obs.LOG_WARNING, f"This is endpoint: {api_endpoint}")
    websocket = websockets.WebSocketApp(api_endpoint,
                                        on_message=on_message,
                                        on_error=on_any_trouble,
                                        on_close=on_any_trouble)
    websocket.run_forever()


def update_text(text):
    global text_source
    global old_text

    if old_text == text:
        return

    source = obs.obs_get_source_by_name(text_source)
    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", text)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

        old_text = text
    else:
        if DEBUG:
            obs.script_log(
                obs.LOG_WARNING, f"Source is empty: {source}/{text_source}")


def check_thread_is_alive():
    global websocket_thread
    global thread_ws_stop

    if websocket_thread is not None:
        if not websocket_thread.is_alive():
            websocket_thread = threading.Thread(target=run_ws)
            websocket_thread.daemon = True
            websocket_thread.start()
            thread_ws_stop = False


def refresh_pressed(props, prop):
    global websocket_thread
    global api_endpoint
    global thread_ws_stop

    obs.timer_remove(check_thread_is_alive)

    if websocket_thread is not None:
        if websocket_thread.is_alive():
            thread_ws_stop = True
            while websocket_thread.is_alive():
                pass

            thread_ws_stop = False

    websocket_thread = threading.Thread(target=run_ws)
    websocket_thread.daemon = True
    websocket_thread.start()

    obs.timer_add(check_thread_is_alive, 1000)


def script_description(): # as the name suggests
    return '''This is script for gathering data from gosumemory!

Requirements:
Python 3.6.x!(THIS IS VERY IMPORTANT)
websocket-client (python -m pip install websocket-client)

Documentation: https://vk.cc/az3XWj
If you have any questions: https://discord.gg/8enr4qD'''


def script_unload():
    global thread_ws_stop
    if websocket_thread is not None:
        if websocket_thread.is_alive():
            thread_ws_stop = True


def save_pressed(props, prop):
    global api_endpoint
    global jsonpath
    global text_source
    global format_rule
    global format_args

    global thread_ws_stop
    global websocket_thread

    api_endpoint = new_state["api_endpoint"]
    jsonpath = new_state["jsonpath"]

    text_source = new_state["text_source"]
    format_rule = new_state["format_rule"]
    format_args = new_state["format_args"]

    if DEBUG:
        obs.script_log(
            obs.LOG_WARNING, f"{new_state}")

    if api_endpoint != "" and text_source != "" and jsonpath != "" and format_rule != "" and format_args:
        obs.timer_remove(check_thread_is_alive)
        if websocket_thread is not None:
            if websocket_thread.is_alive():
                thread_ws_stop = True
                while websocket_thread.is_alive():
                    pass

                thread_ws_stop = False

        websocket_thread = threading.Thread(target=run_ws)
        websocket_thread.daemon = True
        websocket_thread.start()

        obs.timer_add(check_thread_is_alive, 1000)


def script_update(settings): # wtf
    global new_state

    new_state["api_endpoint"] = obs.obs_data_get_string(
        settings, "api_endpoint")
    new_state["jsonpath"] = obs.obs_data_get_string(settings, "jsonpath").replace(" ", "").strip()
    if "," in new_state["jsonpath"]:
        new_state["jsonpath"] = new_state["jsonpath"].split(",")

    new_state["text_source"] = obs.obs_data_get_string(settings, "text_source")
    new_state["format_rule"] = obs.obs_data_get_string(settings, "format_rule")
    if type(new_state["jsonpath"]) == str:
        new_state["format_args"] = [""]
    elif type(new_state["jsonpath"]) in [list, tuple]:
        new_state["format_args"] = []
        for _ in new_state["jsonpath"]:
            new_state["format_args"].append("")


def script_load(settings): # Probably loading stuff, as the name said (ig)
    global new_state

    if DEBUG:
        obs.script_log(
            obs.LOG_WARNING, "I'm joined to the party")

    new_state["api_endpoint"] = obs.obs_data_get_string(
        settings, "api_endpoint")
    new_state["jsonpath"] = obs.obs_data_get_string(settings, "jsonpath").replace(" ", "").strip()
    if "," in new_state["jsonpath"]:
        new_state["jsonpath"] = new_state["jsonpath"].split(",")

    new_state["text_source"] = obs.obs_data_get_string(settings, "text_source")
    new_state["format_rule"] = obs.obs_data_get_string(settings, "format_rule")
    if type(new_state["jsonpath"]) == str:
        new_state["format_args"] = [""]
    elif type(new_state["jsonpath"]) in [list, tuple]:
        new_state["format_args"] = []
        for _ in new_state["jsonpath"]:
            new_state["format_args"].append("")

    if DEBUG:
        obs.script_log(
            obs.LOG_WARNING, f"{new_state}")

    save_pressed(None, None)


def script_defaults(settings): #Default Value in Properties.
    obs.obs_data_set_default_string(
        settings, "api_endpoint", "ws://localhost:24050/ws")
    obs.obs_data_set_default_string(settings, "jsonpath", "menu.state")
    obs.obs_data_set_default_string(
        settings, "format_rule", "State: {0}")

    new_state["jsonpath"] = "menu.state"
    new_state["format_rule"] = "State: {0}"
    new_state["api_endpoint"] = "ws://localhost:24050/ws"


def script_properties(): # Properties Screen (ig)
    props = obs.obs_properties_create()

    # obs_property_t *obs_properties_add_text(obs_properties_t *props, const char *name, const char *description, enum obs_text_type type)
    obs.obs_properties_add_text(
        props, "api_endpoint", "API Endpoint", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        props, "jsonpath", "Path to json string (ex menu.state)", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(
        props, "format_rule", "Formatting rule (python format)", obs.OBS_TEXT_MULTILINE)
    # obs_property_t *obs_properties_add_int(obs_properties_t *props, const char *name, const char *description, int min, int max, int step)

    p = obs.obs_properties_add_list(
        props, "text_source", "Text Source (old FreeType 2)", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_ft2_source":
            # gdiplus lags!!!!!! if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_button(
        props, "button", "Save/Refresh", save_pressed)
    return props
