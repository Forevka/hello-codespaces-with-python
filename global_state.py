from enum import Enum
import datetime
from config import wait_before_restart, cooldown_after_restart

class States(Enum):
    RESTARTING = "restarting"
    RESTART_IN_PERIOD = "restart_in_period"
    RESTART_STARTED_AT = "restart_started_at"
    RESTART_COOLDOWN = "restart_cooldown"
    RESTART_IN_COOLDOWN = "restart_in_cooldown"

class State:
    instance: 'State' = None

    state = {
        States.RESTARTING: False,
        States.RESTART_IN_PERIOD: datetime.timedelta(minutes=wait_before_restart),
        States.RESTART_STARTED_AT: datetime.datetime.now(),
        States.RESTART_IN_COOLDOWN: False,
        States.RESTART_COOLDOWN: datetime.timedelta(minutes=cooldown_after_restart),
    }

state = State.state
