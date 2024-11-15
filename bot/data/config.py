# - *- coding: utf- 8 - *-
import configparser
import json

BOT_CONFIG = configparser.ConfigParser()
BOT_CONFIG.read("settings.ini")

BOT_TOKEN = BOT_CONFIG['bot_settings']['token'].strip().replace(' ', '')
BOT_TEXTS = json.load(open('texts.json', 'r', encoding='utf-8'))

USER_TABLE_ID = BOT_CONFIG['google_settings']['user_table_id']
ORDERS_TABLE_ID = BOT_CONFIG['google_settings']['orders_table_id']

def get_admins() -> list[int]:
    read_admins = configparser.ConfigParser()
    read_admins.read("settings.ini")

    admins = read_admins['bot_settings']['admin_id'].strip().replace(" ", "")

    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins: admins.remove("")
    while " " in admins: admins.remove(" ")
    while "\r" in admins: admins.remove("\r")
    while "\n" in admins: admins.remove("\n")

    admins = list(map(int, admins))

    return admins
