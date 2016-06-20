# coding=UTF-8
""" Settings File """
import logging

CONFIG = {
    "LOG_LEVEL": logging.WARN,

    "TELEGRAM_START_COMMAND": "start",
    "MENU_APP_TEXT": "Application",
    "MENU_OS_TEXT": "OS",
    "HOME_TEXT": "Back to home",
    "LANGUAGE_FILE": "lang.json",
    "ITEMS_PER_ROW": 3,
    "MAX_ITEMS_PER_ROW": 4,
    "MSG_TIMEOUT": 33,
    "APPLICATION_SOURCE": "",
    "ACTION_NAME": "get-file",

    "S3_CONF_BUCKET_KEY": "config.pb2",
    "S3_BUCKET_NAME": "",
    "S3_CREDENTIAL_FILE": "conf_access.json",
    "MAX_ALLOWED_FILE_SIZE": 45000000
}
