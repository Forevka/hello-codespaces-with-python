import asyncio
from update_mods import update_mods

app_id = 108600
path_to_wokshop_acf = './appworkshop_108600.acf'

async def main():
    await update_mods(path_to_wokshop_acf)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
