from update_mods import check_mods_to_update
import subprocess
from rcon import Client

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
subprocess.Popen(["mybatchfile.bat"])

path_to_wokshop_acf = './appworkshop_108600.acf'
rcon_host = '127.0.0.1'
rcon_port = 27015
rcon_password = "werdwerd"

app = FastAPI()

@app.on_event("startup")
@repeat_every(seconds=20)
async def remove_expired_tokens_task() -> None:
    mods_to_update = await check_mods_to_update(path_to_wokshop_acf)
    
    with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
        response = client.run('servermsg', 'restart in 5 min')
        print(response)



#servermsg test

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())
