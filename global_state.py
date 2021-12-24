from enum import Enum
import datetime
from config import wait_before_restart, cooldown_after_restart

class States(Enum):
    RESTARTING = "restarting"
    RESTART_IN_PERIOD = "restart_in_period"
    RESTART_STARTED_AT = "restart_started_at"
    RESTART_COOLDOWN = "restart_cooldown"
    RESTART_IN_COOLDOWN = "restart_in_cooldown"
    RESTART_DISCORD_NOTIFICATIONS = "restart_discord_notifications"
    RESTART_PLANNED = "restart_planned"

    SERVER_WAITING_TO_START = "server_waiting_to_start"


class State:
    instance: 'State' = None

    state = {
        States.RESTARTING: False,
        States.RESTART_IN_PERIOD: datetime.timedelta(minutes=wait_before_restart),
        States.RESTART_STARTED_AT: datetime.datetime.now(),
        States.RESTART_IN_COOLDOWN: False,
        States.RESTART_COOLDOWN: datetime.timedelta(minutes=cooldown_after_restart),
        States.RESTART_DISCORD_NOTIFICATIONS: [],
        States.RESTART_PLANNED: False,
        States.SERVER_WAITING_TO_START: False
    }
    
state = State.state
