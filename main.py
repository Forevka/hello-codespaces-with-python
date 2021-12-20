import datetime
from update_mods import check_mods_to_update
import subprocess
from rcon import Client
import humanize
import logging
from logging.handlers import RotatingFileHandler

from global_state import state, States

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from utils import round_time

path_to_server_bat_file = "E:\SteamLibrary\steamapps\common\ProjectZomboid\ProjectZomboidServer.bat"
path_to_wokshop_acf = './appworkshop_108600.acf'
rcon_host = '127.0.0.1'
rcon_port = 27015
rcon_password = "werdwerd"
address = (rcon_host, rcon_port)

app = FastAPI()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)

api_file_rotator = RotatingFileHandler('./logs/api_logger.log', maxBytes=1000 * 100, backupCount=10)
api_file_rotator.setFormatter(formatter)

api_logger.addHandler(api_file_rotator)

zomboid_logger = logging.getLogger('zomboid')
zomboid_logger.setLevel(logging.DEBUG)

zomboid_file_rotator = RotatingFileHandler('./logs/zomboid_logger.log', maxBytes=1000 * 100, backupCount=10)
zomboid_file_rotator.setFormatter(formatter)

zomboid_logger.addHandler(zomboid_file_rotator)

@app.on_event("startup")
@repeat_every(seconds=20)
async def remove_expired_tokens_task() -> None:
    api_logger.info("BEFORE", state)
    if (state[States.RESTART_IN_COOLDOWN]):
        api_logger.info("RESTART COOLDOWN BEFORE", state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN])
        state[States.RESTART_IN_COOLDOWN] = state[States.RESTART_STARTED_AT] + state[States.RESTART_COOLDOWN] > datetime.datetime.now()
        return


    if not state[States.RESTARTING]:
        mods_to_update = await check_mods_to_update(path_to_wokshop_acf)

        if (mods_to_update):
            #print('Mods to update', mods_to_update)
            state[States.RESTARTING] = True
            state[States.RESTART_STARTED_AT] = datetime.datetime.now()
            
    if state[States.RESTARTING]:
        with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
            try:
                restart_in: datetime.timedelta = -(datetime.datetime.now() - state[States.RESTART_STARTED_AT]) + (state[States.RESTART_IN_PERIOD])
                api_logger.info('Restarts in:', restart_in)
                response = client.run('servermsg', f'"[Mod update] Server restart in {humanize.naturaldelta(datetime.timedelta(minutes = round(restart_in.total_seconds() / 60)))}"')

                if datetime.datetime.now() >= state[States.RESTART_STARTED_AT] + state[States.RESTART_IN_PERIOD]:
                    state[States.RESTART_IN_COOLDOWN] = True
                    state[States.RESTARTING] = False
                    client.run('quit')
                    subprocess.Popen([path_to_server_bat_file], stdout=zomboid_logger.info, stderr=zomboid_logger.error)
            except Exception as e:
                api_logger.error(e)
                
    api_logger.info("AFTER", state)

#servermsg test

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())
