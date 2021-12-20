from enum import Enum
import datetime

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
        States.RESTART_IN_PERIOD: datetime.timedelta(minutes=2),
        States.RESTART_STARTED_AT: datetime.datetime.now(),
        States.RESTART_IN_COOLDOWN: False,
        States.RESTART_COOLDOWN: datetime.timedelta(minutes=10),
    }

state = State.state
