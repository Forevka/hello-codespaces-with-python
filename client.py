import aiohttp

class Client:
    session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession, urls_dict):
        self.session = session
        self.urls_dict = urls_dict

    async def get(self, url: str, *args,):
        async with self.session.get(url.format(*args)) as resp:
            return await resp.text()

    async def get_changelog(self, mod_id: int):
        return await self.get(self.urls_dict["changelog"], mod_id)
