import datetime
import discord
from logger_config import discord_bot_logger
from global_state import state, States
from config import discord_bot_admins, path_to_wokshop_acf, steam_mod_changelog_url
from update_mods import check_mods_to_update


class AfterBattleClient(discord.Client):
    async def on_ready(self):
        discord_bot_logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        discord_bot_logger.info('Message from {0.author}: {0.content}'.format(message))
        
        if (message.author.id not in discord_bot_admins):
            discord_bot_logger.info(f'{message.author} trying to speak with bot, ignoring')
            return 

        if message.content.startswith('!debug'):
            text = ""
            for key, value in state.items():
                text += f"{key.value}: {str(value)}\n"

            await message.reply(text)

        if message.content.startswith('!force_restart'):
            state[States.RESTARTING] = True
            state[States.RESTART_STARTED_AT] = datetime.datetime.now()

        if message.content.startswith('!check_updates'):
            mods_to_update = await check_mods_to_update(path_to_wokshop_acf)
            message_text = '\n'.join([f"[{i['name']}]({steam_mod_changelog_url.format(i['mod_id'])})" for i in mods_to_update])
            e = discord.Embed(title=f'Всего {len(mods_to_update)}', description=message_text)
            await message.reply(f"Проверка завершена, результаты:", embed=e)

        if message.content.startswith('!help'):
            await message.reply("""
!debug - show global state
!force_restart - restart server in particular scheduled way
!check_updates - bot will send how many mods need to update
            """)

ds_client = AfterBattleClient(allowed_mentions = discord.AllowedMentions(everyone = True))
