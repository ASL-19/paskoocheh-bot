""" Telegram Bot handler's main entry point
"""
import logging
import json
import sys
import time

from os import sys, path
from pyskoocheh import storage, actionlog, telegram
from settings import CONFIG
import protobuf.schemas.python.paskoocheh_pb2 as paskoocheh

sys.path.append(path.dirname(path.abspath(".")))
LOGGER = logging.getLogger()
LOGGER.setLevel(CONFIG["LOG_LEVEL"])

def make_app_os_text(app_name, os_name):
    """ Makes the text to send as Application + OS
        to show as a keyboard button
        app: app name
        os: OS the app is written for
    """
    name = paskoocheh.PlatformName.Name(os_name).title()
    return app_name + " (" + name + ")"

def parse_conf_data(conf):
    """ Parses the cofiguration data and creates the
        dictionary of apps and OSes to show to the user
        conf: the configuration json structure
    """
    namelist = []
    oslist = []
    applistname = {}
    applistos = {}
    apposlist = {}

    if not conf:
        LOGGER.error("Configuration file is empty")
        return None, None, None

    for platform in conf.platforms:
        name = paskoocheh.PlatformName.Name(platform.name).title()
        if not platform.tools:
            continue
        if name not in oslist:
            oslist.append(name)
            applistos[name] = []
        for tool in platform.tools:
            if tool.contact.name not in namelist:
                namelist.append(tool.contact.name)
                applistname[tool.contact.name] = []

            apposlist[make_app_os_text(tool.contact.name, platform.name)] = {
                "app": tool.contact.name,
                "os": name,
                "key": tool.releases[0].binary.path,
                "filename": path.basename(tool.releases[0].binary.path),
                "release_url": tool.releases[0].release_url
            }
            applistos[name].append(tool.contact.name)
            applistname[tool.contact.name].append(name)
    LOGGER.info(apposlist)

    return applistname, applistos, apposlist

def bot_handler(event, _):
    """ Main entry point to handle the bot
        event: information about the chat
        _: information about the telegram message (unused)
    """
    LOGGER.info("%s:%s Request received:%s", __name__, str(time.time()), str(event))

    msg_date = event["Input"]["message"]["date"]
    msg_id = int(event["Input"]["message"]["message_id"])
    chat_id = int(event["Input"]["message"]["chat"]["id"])
    command = ""
    try:
        msg = event["Input"]["message"]["text"]
    except KeyError as error:
        LOGGER.error("There is no message text, exiting...")
        return None

    try:
        language = event["lang"]
        LOGGER.info("Language is %s", event["lang"])
    except KeyError as error:
        language = "fa"
        LOGGER.info("Language is not defined!")

    try:
        token = event["token"]
    except KeyError as error:
        LOGGER.error("Token is not defined!")
        return None

    if time.time() > msg_date + CONFIG["MSG_TIMEOUT"]:
        LOGGER.error("Old message ignoring now %s msg_date %s)", time.time(), msg_date)
        return None

    lang = {}
    try:
        with open(CONFIG["LANGUAGE_FILE"]) as lang_file:
            lang = json.load(lang_file)
    except IOError as error:
        LOGGER.error("Unable to open file for reading %s (Error: %s:%s)",
                     CONFIG["LANGUAGE_FILE"], error.errno, error.strerror)
        telegram.send_message(token, chat_id, "There seems to be something wrong with my language!")
        return None

    # Read configuration Data from S3
    pb_file = storage.get_binary_contents(CONFIG["S3_BUCKET_NAME"], CONFIG["S3_CONF_BUCKET_KEY"])
    conf_file = paskoocheh.Config()
    conf_file.ParseFromString(pb_file["Body"].read())
    if not conf_file:
        telegram.send_message(token, chat_id, lang["MSG_ERROR"][language])
        return None

    # Parse Configuration Data for App and OS
    applistname, applistos, apposlist = parse_conf_data(conf_file)
    if applistname is None or applistos is None or apposlist is None:
        telegram.send_message(token, chat_id, lang["MSG_ERROR"][language])
        return None

    if msg[0] == "/":
        command = msg[1:].lower()

    if msg == CONFIG["HOME_TEXT"]:
        command = CONFIG["TELEGRAM_START_COMMAND"]

    LOGGER.info("Message: %s MessageId: %s ChatId: %s Command: %s",
                msg, str(msg_id), str(chat_id), command)

    if command == CONFIG["TELEGRAM_START_COMMAND"]:
        keyboard = [[CONFIG["MENU_OS_TEXT"], CONFIG["MENU_APP_TEXT"]]]
        telegram.send_keyboard(token, chat_id, lang["MSG_START_COMMAND"][language], keyboard)
    elif command == "":
        # This is a message not started with /
        if msg == CONFIG["MENU_APP_TEXT"]:
            LOGGER.info("App selected")
            items = []
            for app in applistname:
                items.append(app)

            keyboard = telegram.make_keyboard(items, CONFIG["ITEMS_PER_ROW"])
            telegram.send_keyboard(token, chat_id, lang["MSG_SELECT_APP"][language], keyboard)
            return None
        elif msg == CONFIG["MENU_OS_TEXT"]:
            LOGGER.info("OS selected")
            items = []
            for os_name in applistos:
                items.append(os_name)

            keyboard = telegram.make_keyboard(items, CONFIG["ITEMS_PER_ROW"])
            LOGGER.info("os keyboard: %s", keyboard)
            telegram.send_keyboard(token, chat_id, lang["MSG_SELECT_OS"][language], keyboard)
            return None
        else:
            for app_name, oses in applistname.iteritems():
                if msg == app_name:
                    LOGGER.info("User asked for app name %s returning os list: %s", app_name, oses)
                    texts = ["{} ({})".format(app_name, os_name) for os_name in oses]
                    keyboard = telegram.make_keyboard(texts, CONFIG["ITEMS_PER_ROW"])
                    telegram.send_keyboard(token, chat_id, lang["MSG_SELECT_APPOS"][language],
                                           keyboard)
                    return None

            for os_name, apps in applistos.iteritems():
                if msg == os_name:
                    LOGGER.info("User asked for os name %s returning app list: %s", os_name, apps)
                    texts = ["{} ({})".format(app_name, os_name) for app_name in apps]
                    keyboard = telegram.make_keyboard(texts, CONFIG["ITEMS_PER_ROW"])
                    telegram.send_keyboard(token, chat_id, lang["MSG_SELECT_APPOS"][language],
                                           keyboard)
                    return None

            for appos, values in apposlist.iteritems():
                if msg == appos:
                    action_name = values["filename"]
                    if action_name == "":
                        action_name = values["release_url"]
                    LOGGER.info("User requested %s, sending file: %s",
                                msg, values["filename"])
                    if actionlog.is_limit_exceeded(chat_id, action_name):
                        telegram.send_message(token, chat_id,
                                              lang["FILE_LIMIT_EXCEEDED"][language])
                        keyboard = [[CONFIG["MENU_OS_TEXT"], CONFIG["MENU_APP_TEXT"]]]
                        telegram.send_keyboard(token, chat_id,
                                               lang["MSG_START_COMMAND"][language], keyboard)
                        return None
                    else:
                        key = values["key"].strip("/")
                        if not key or key == "":
                            link = values["release_url"]
                            meta = {
                                "content_length": CONFIG["MAX_ALLOWED_FILE_SIZE"]
                            }
                            telegram.send_message(token, chat_id,
                                                  lang["MSG_FILE_DOWNLOAD"][language] +
                                                  "\n" + link, [[link]])

                            keyboard = [[CONFIG["MENU_OS_TEXT"], CONFIG["MENU_APP_TEXT"]]]
                            telegram.send_keyboard(token, chat_id,
                                                   lang["MSG_START_COMMAND"][language], keyboard)
                            return None

                        """ S3 Serve or Link """
                        link = storage.build_static_link(CONFIG["S3_BUCKET_NAME"], key)
                        meta = storage.get_object_metadata(CONFIG["S3_BUCKET_NAME"], key)

                        if meta.content_length < CONFIG["MAX_ALLOWED_FILE_SIZE"]:
                            telegram.send_message(token, chat_id,
                                                  lang["MSG_WAIT"][language])

                            if values["os"].lower() == "windows":
                                telegram.send_message(token, chat_id,
                                                  lang["MSG_WINDOWS_TEXT_FILE"][language])

                            telegram.send_file(token, chat_id,
                                               lang["MSG_FILE_DOWNLOAD"][language] +
                                               "\n" + link, CONFIG["S3_BUCKET_NAME"], key)
                        else:
                            LOGGER.info("File too large, sending link")
                            with open(CONFIG["S3_CREDENTIAL_FILE"]) as conf_sec:
                                conf_access = json.load(conf_sec)

                            api_key_id = conf_access["LIMITED_ACCESS"]["API_KEY_ID"]
                            secret_key = conf_access["LIMITED_ACCESS"]["SECRET_KEY"]
                            temp_link = storage.get_temp_link(CONFIG["S3_BUCKET_NAME"], key,
                                                              api_key_id, secret_key)
                            temp_link = temp_link.replace("https://paskoocheh.s3.amazonaws.com/", "https://s3.amazonaws.com/paskoocheh/")
                            telegram.send_message(token, chat_id,
                                                  lang["MSG_FILE_DOWNLOAD"][language] +
                                                  "\n" + temp_link, [[temp_link]])
                        actionlog.log_action(str(chat_id), action_name,
                                             CONFIG["APPLICATION_SOURCE"])

                    keyboard = [[CONFIG["MENU_OS_TEXT"], CONFIG["MENU_APP_TEXT"]]]
                    telegram.send_keyboard(token, chat_id,
                                           lang["MSG_START_COMMAND"][language], keyboard)
                    return None
            telegram.send_message(token, chat_id, lang["MSG_CHITCHAT"][language])
