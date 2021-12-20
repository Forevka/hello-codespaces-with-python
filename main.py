import datetime
from update_mods import check_mods_to_update
import subprocess
from rcon import Client
import humanize
import asyncio
import threading

from global_state import state, States

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from logger_config import api_logger, zomboid_logger

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        zomboid_logger.info(line)

zomboid_process = None
zomboid_thread = None

def start_zomboid_server_wait_end():
    global zomboid_process, zomboid_thread
    api_logger.warning(f'zomboid process starting')
    zomboid_process = subprocess.Popen([path_to_server_bat_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    with zomboid_process.stdout:
        log_subprocess_output(zomboid_process.stdout)
    exitcode = zomboid_process.wait()
    api_logger.warning(f'zomboid process exited with: {exitcode}')

path_to_server_bat_file = "E:\SteamLibrary\steamapps\common\ProjectZomboid\ProjectZomboidServer.bat"
path_to_wokshop_acf = './appworkshop_108600.acf'
rcon_host = '127.0.0.1'
rcon_port = 27015
rcon_password = "werdwerd"

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
def start_zomboid():
    global zomboid_process, zomboid_thread
    zomboid_thread = threading.Thread(target=start_zomboid_server_wait_end)
    zomboid_thread.start()


@app.on_event("startup")
@repeat_every(seconds=40, wait_first=True)
async def remove_expired_tokens_task() -> None:
    global zomboid_process, zomboid_thread
    api_logger.info(f"BEFORE {state}", )
    if (state[States.RESTART_IN_COOLDOWN]):
        api_logger.info(f"RESTART COOLDOWN BEFORE {state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN]}", )
        state[States.RESTART_IN_COOLDOWN] = state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN] > datetime.datetime.now()
        return


    if not state[States.RESTARTING]:
        mods_to_update = await check_mods_to_update(path_to_wokshop_acf)

        if (mods_to_update):
            state[States.RESTARTING] = True
            state[States.RESTART_STARTED_AT] = datetime.datetime.now()
            
    if state[States.RESTARTING]:
        with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
            try:
                restart_in: datetime.timedelta = -(datetime.datetime.now() - state[States.RESTART_STARTED_AT]) + (state[States.RESTART_IN_PERIOD])
                api_logger.info(f'Restarts in: {restart_in}')
                response = client.run('servermsg', f'"[Mod update] Server restart in {humanize.naturaldelta(datetime.timedelta(minutes = round(restart_in.total_seconds() / 60)))}"')

                if datetime.datetime.now() >= state[States.RESTART_STARTED_AT] + state[States.RESTART_IN_PERIOD]:
                    state[States.RESTART_IN_COOLDOWN] = True
                    state[States.RESTARTING] = False
                    client.run('quit')
                    api_logger.info('waiting server to stop...')
                    await asyncio.sleep(10)
                    api_logger.info('starting new instance of PZ server')
                    zomboid_thread = threading.Thread(target=start_zomboid_server_wait_end)
                    zomboid_thread.start()
                    
            except Exception as e:
                api_logger.error(e)
                
    api_logger.info(f"AFTER {state}")

#servermsg test

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())
