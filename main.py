import datetime
import json

import discord
from update_mods import check_mods_to_update
import subprocess
from rcon import Client
import humanize
import asyncio
import threading
from notifiers.discord_bot import ds_client
from client import Client as ApiClient

from global_state import state, States

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from logger_config import api_logger
from config import (
    path_to_server_bat_file,
    path_to_wokshop_acf,
    discord_bot_token,
    rcon_host,
    rcon_password,
    rcon_port,
    discord_channel_for_notifiers,
    steam_mod_changelog_url,
    wait_before_restart,
    discord_notification_points,
    planned_restart_every_seconds,
    planned_restart_at,
    current_time_url,
    timezone,
)
from utils import log_subprocess_output

zomboid_process = None
zomboid_thread = None


def start_zomboid_server_wait_end():
    global zomboid_process, zomboid_thread
    api_logger.warning(f"zomboid process starting")
    zomboid_process = subprocess.Popen(
        [path_to_server_bat_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
    )
    with zomboid_process.stdout:
        log_subprocess_output(zomboid_process.stdout)
    exitcode = zomboid_process.wait()
    api_logger.warning(f"zomboid process exited with: {exitcode}")


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
@repeat_every(seconds=3, wait_first=True)
async def is_zomboid_server_running() -> None:
    if (state[States.SERVER_WAITING_TO_START] == True):
        try:
            with Client(rcon_host, rcon_port, passwd=rcon_password, timeout=2) as client:
                client.run("players")
                state[States.SERVER_WAITING_TO_START] = False

                channel = ds_client.get_channel(discord_channel_for_notifiers)
                await channel.send("Сервер перезапущен, можно играть.")
        except TimeoutError as e:
            api_logger.warning('server not started yet')
        except Exception as ee:
            api_logger.exception('error', ee)



@app.on_event("startup")
async def start_zomboid():
    global zomboid_process, zomboid_thread
    zomboid_thread = threading.Thread(target=start_zomboid_server_wait_end)
    zomboid_thread.start()

    asyncio.create_task(ds_client.start(discord_bot_token))

@app.on_event("startup")
@repeat_every(seconds=planned_restart_every_seconds, wait_first=True)
async def planned_restart_every_n_seconds() -> None:
    urls = {
        "changelog": steam_mod_changelog_url,
        "current_time": current_time_url,
    }

    client = ApiClient(urls)

    internet_time = await client.get_current_time(timezone)
    loaded_time = json.loads(internet_time)
    current_time = datetime.datetime.fromisoformat(loaded_time['datetime'])

    if (current_time.hour in planned_restart_at) and (current_time.hour != state[States.RESTART_PLANNED_STARTED_AT].hour):
        state[States.RESTART_PLANNED] = True
        state[States.RESTARTING] = True
        state[States.RESTART_STARTED_AT] = datetime.datetime.now()
        state[States.RESTART_PLANNED_STARTED_AT] = datetime.datetime.now()

        channel = ds_client.get_channel(discord_channel_for_notifiers)
        await channel.send(f"*Внимание* плановый рестарт сервера, @everyone. Сервер перезапустится через {wait_before_restart}",)
        
        api_logger.info(f"starting planned restart, because now {current_time.hour} by {timezone}")


@app.on_event("startup")
@repeat_every(seconds=20, wait_first=True)
async def check_mod_updates_and_restart() -> None:
    global zomboid_process, zomboid_thread
    api_logger.info(f"BEFORE {state}")
    if (state[States.SERVER_WAITING_TO_START] == True):
        api_logger.info(f"Waiting server to start, skipping mod check")

        return

    try:
        if state[States.RESTART_IN_COOLDOWN]:
            api_logger.info(f"RESTART COOLDOWN BEFORE {state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN]}")
            state[States.RESTART_IN_COOLDOWN] = (
                state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN]
                > datetime.datetime.now()
            )
            return

        if not state[States.RESTARTING]:
            mods_to_update = await check_mods_to_update(path_to_wokshop_acf)

            if mods_to_update:
                state[States.RESTARTING] = True
                state[States.RESTART_STARTED_AT] = datetime.datetime.now()
                channel = ds_client.get_channel(discord_channel_for_notifiers)
                message = '\n'.join([f"[{i['name']}]({steam_mod_changelog_url.format(i['mod_id'])})" for i in mods_to_update])
                e = discord.Embed(title=f'Всего {len(mods_to_update)}', description=message)
                await channel.send(f"Есть моды которые нужно обновить, @everyone. Сервер перезапустится через {wait_before_restart} минут.\nПросим всех перезайти в игру чтобы обновиться.", embed=e)

        if state[States.RESTARTING]:
            with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
                try:
                    restart_in: datetime.timedelta = -(datetime.datetime.now() - state[States.RESTART_STARTED_AT]) + (state[States.RESTART_IN_PERIOD])
                    api_logger.info(f"Restarts in: {restart_in}")
                    restart_in_rounded_minutes = datetime.timedelta(minutes = round(restart_in.total_seconds() / 60))

                    is_mod_update = state[States.RESTART_PLANNED] == False

                    server_notification_msg = f'"[Mod update] Server restart in {humanize.naturaldelta(restart_in_rounded_minutes)}"' if is_mod_update else f'"[Planned restart] Server restart in {humanize.naturaldelta(restart_in_rounded_minutes)}"'

                    response = client.run(
                        "servermsg",
                        server_notification_msg,
                    )

                    notification_breakpoint = restart_in_rounded_minutes.total_seconds() / 60
                    if notification_breakpoint not in state[States.RESTART_DISCORD_NOTIFICATIONS]:
                        discord_notification = discord_notification_points.get(notification_breakpoint, None)
                        if discord_notification:
                            channel = ds_client.get_channel(discord_channel_for_notifiers)
                            await channel.send(discord_notification)

                        state[States.RESTART_DISCORD_NOTIFICATIONS].append(restart_in_rounded_minutes.total_seconds() / 60)

                    if (datetime.datetime.now() >= state[States.RESTART_STARTED_AT] + state[States.RESTART_IN_PERIOD]):
                        state[States.RESTART_IN_COOLDOWN] = True
                        state[States.RESTARTING] = False
                        state[States.RESTART_DISCORD_NOTIFICATIONS] = []
                        state[States.RESTART_PLANNED] = False

                        client.run("quit")
                        
                        api_logger.info("waiting server to stop...")
                        await asyncio.sleep(10)
                        api_logger.info("starting new instance of PZ server")
                        zomboid_thread = threading.Thread(
                            target=start_zomboid_server_wait_end
                        )
                        zomboid_thread.start()

                        state[States.SERVER_WAITING_TO_START] = True
                except Exception as e:
                    api_logger.error(e)

        api_logger.info(f"AFTER {state}")
    except Exception as e:
        api_logger.error(e)

