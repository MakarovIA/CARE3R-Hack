from enum import Enum

from config import *


class UserGlobalStatus(Enum):
    OK=1
    PRE_DISASTER=2
    IN_DISASTER=3
    POST_DISASTER=4


def init_user_db():
    return {
        DEFAULT_USER: {'location': DEFAULT_LOCATION, 'status': UserGlobalStatus.OK, 'coords': DEFAULT_COORDS, 'msgs': []},
        POST_DEFAULT_USER: {'location': POST_DEFAULT_LOCATION, 'status': UserGlobalStatus.POST_DISASTER,
                            'coords': POST_DEFAULT_COORDS, 'msgs': []},
        LOCAL_USER: {'location': LOCAL_DEFAULT_LOCATION, 'status': UserGlobalStatus.IN_DISASTER,
                            'coords': POST_DEFAULT_COORDS, 'msgs': []},
    }


user_to_global_status = init_user_db()
