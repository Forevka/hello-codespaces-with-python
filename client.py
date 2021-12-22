import aiohttp

class Client:
    def __init__(self, urls_dict):
        self.urls_dict = urls_dict

    async def get(self, url: str, *args,):
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(*args)) as resp:
                return await resp.text()

    async def get_changelog(self, mod_id: int):
        return await self.get(self.urls_dict["changelog"], mod_id)
