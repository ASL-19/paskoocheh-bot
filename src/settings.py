# coding=UTF-8
""" Settings File """
import logging

CONFIG = {
    "LOG_LEVEL": logging.WARN,

    "TELEGRAM_START_COMMAND": "start",
    "PASK_APK_KEY": "",
    "LANGUAGE_FILE": "lang.json",
    "ITEMS_PER_ROW": 3,
    "MAX_ITEMS_PER_ROW": 4,
    "MSG_TIMEOUT": 33,
    "APPLICATION_SOURCE": "",
    "ACTION_NAME": "get-file",
    "CLICKSTREAM_TABLE": "",

    "S3_REGION": "",
    "S3_CONF_BUCKET_KEY": "",
    "S3_BUCKET_NAME": "",
    "S3_CREDENTIAL_FILE": "conf_access.json",
    "S3_PROMO_BUCKET_NAME": "",
    "S3_PROMO_FILE_EXTENSION": "",
    "MAX_ALLOWED_FILE_SIZE": 45000000
}
