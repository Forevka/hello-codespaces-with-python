import asyncio
from update_mods import update_mods

app_id = 108600
path_to_wokshop_acf = './appworkshop_108600.acf'
steamcmd_path = './steamcmd/directory'
path_to_mods = './path/to/steam'

async def main():
    await update_mods(app_id, path_to_mods, steamcmd_path, path_to_wokshop_acf)

asyncio.get_event_loop().run_until_complete(main())