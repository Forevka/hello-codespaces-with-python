import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime
from acf import loads as load_acf
from steamcmd import Steamcmd
import os

from client import Client



async def load_mod_info(client, mod_id,):
    raw_changelog = await client.get_changelog(mod_id)
    soup = BeautifulSoup(raw_changelog, 'lxml')

    latest_change = soup.find('div', class_='changelog headline')
    human_datetime = re.sub(r'\t', '',  latest_change.text)
    human_datetime = re.sub(r'\n', '',  human_datetime)
    human_datetime = re.sub(r'\r', '',  human_datetime).replace('Update: ', '').replace('@', '').replace('  ', ' ')

    mod_name = soup.find('div', class_='workshopItemTitle')
    print('Mod name: ', mod_name.text)
    #print('Steam latest update datetime: ', human_datetime)

    with_year = human_datetime.find(',') > 0
    if with_year:
        change_datetime = datetime.strptime(human_datetime, '%d %b, %Y %I:%M%p')
    else:
        change_datetime = datetime.strptime(human_datetime, '%d %b %I:%M%p')
        change_datetime = datetime(datetime.now().year, change_datetime.month, change_datetime.day, change_datetime.hour, change_datetime.minute)

    print('Last updated at: ', change_datetime)

    return {
        "name": mod_name.text,
        "last_update": change_datetime,
        "last_update_timestamp": change_datetime.timestamp()
    }

async def info_wrapper(mod_id, list_to_update, client, workshop_local_items):
    mod_info = await load_mod_info(client, mod_id)
    #print(mod_info)
    local_mod_info = workshop_local_items['AppWorkshop']['WorkshopItemsInstalled'][mod_id]
    local_installed_at_timestamp = datetime.fromtimestamp(int(local_mod_info['timeupdated']))
    print('Local installed updated at: ', local_installed_at_timestamp)
    if mod_info["last_update"] > local_installed_at_timestamp:
        print('NEED UPDATE ', mod_info['name'])
        list_to_update.append(mod_id)
    else:
        print('up to date, ok')

async def update_mods(app_id, path_to_mods, steamcmd_path, path_to_wokshop_acf):
    acf = open(path_to_wokshop_acf, 'r', encoding="utf-8")

    workshop_local_items = load_acf(acf.read())

    local_mods = list(workshop_local_items['AppWorkshop']['WorkshopItemsInstalled'].keys())

    urls = {
        "changelog": "https://steamcommunity.com/sharedfiles/filedetails/changelog/{}"
    }

    session = aiohttp.ClientSession()
    client = Client(session, urls)

    mods_to_update = []

    tasks = [info_wrapper(mod_id, mods_to_update, client, workshop_local_items) for mod_id in local_mods]

    await asyncio.gather(*tasks)

    print('Total mods to update: ', len(mods_to_update))
    if mods_to_update:
        steamcmd = Steamcmd(steamcmd_path)
        for mod_id in mods_to_update:
            steamcmd.install_workshopfiles(app_id, mod_id, path_to_mods)

    await client.session.close()

