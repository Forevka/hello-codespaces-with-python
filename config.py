import os

path_to_server_bat_file = "E:\SteamLibrary\steamapps\common\ProjectZomboid\ProjectZomboidServer.bat"

path_to_wokshop_acf = "./appworkshop_108600.acf"
rcon_host = "127.0.0.1"
rcon_port = 27015
rcon_password = "werdwerd"

wait_before_restart = 5  # minutes
cooldown_after_restart = 10  # minutes

log_file_max_size = 24 # megabytes

path_to_logs = "./logs/"
if not os.path.exists(path_to_logs):
    os.makedirs(path_to_logs)

zomboid_logs_filename = "zomboid_logger.log"
api_logs_filename = "api_logger.log"
discord_logs_filename = "discord_logger.log"

discord_channel_for_notifiers = 923165182581174284
discord_bot_token = "OTIzMTM3MjQ5NDM1MDY2Mzc5.YcLojw.xQKqwewgC9EVSM0w6Kavw1oONNQ"
discord_notification_points = {
    3: "*Внимание!*\nСервер перезапустится через 3 минуты",
    1: "*Внимание!*\nСервер перезапустится через 1 минуту",
}
discord_bot_admins = [464801064781348864, 280349685510832129]

planned_restart_every_seconds = 60 * 60 * 4 # 4 hours

## don't change pls
steam_mod_changelog_url = "https://steamcommunity.com/sharedfiles/filedetails/changelog/{}"steam_mod_changelog_url = "https://steamcommunity.com/sharedfiles/filedetails/changelog/{}"
