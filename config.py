# --- imports ---

import json
import os
from datetime import datetime

from classes import UserInfo, Squad


# --- global variables ---

TEST: bool = True



# --- paths ---

MAIN_DIR = 'data'
TEST_DIR = 'testdata'

USERS_LOCATION = f'{TEST_DIR}/users.json' if TEST else f'{MAIN_DIR}/users.json'
SQUADS_LOCATION = f'{TEST_DIR}/squads.json' if TEST else f'{MAIN_DIR}/squads.json'
EVENTS_DATA_LOCATION = f'{TEST_DIR}/events_data.json' if TEST else f'{MAIN_DIR}/events_data.json'


# --- classes ---

class Data:
    def __init__(self, users: dict[int, UserInfo] | None = None, squads: dict[str, Squad] | None = None, events_data: dict[str, datetime] | None = None):
        self.users = users
        self.squads = squads
        self.events_data = events_data


# --- load & save ---

def load() -> Data:
    users_dict = {}
    squads_dict = {}
    events_data_dict = {}

    try:
        if os.path.exists(USERS_LOCATION):
            with open(USERS_LOCATION, "r") as f:
                users_json = json.load(f)
            for user_id_str, user_info_dict in users_json.items():
                users_dict[int(user_id_str)] = UserInfo.from_json_serializable(user_info_dict)
    except Exception as e:
        print(f'Ошибка при загрузке {USERS_LOCATION}:\n{e}')

    try:
        if os.path.exists(SQUADS_LOCATION):
            with open(SQUADS_LOCATION, "r") as f:
                squads_json = json.load(f)
            for squad_uuid, squad_dict in squads_json.items():
                squads_dict[squad_uuid] = Squad.from_json_serializable(squad_dict)
    except Exception as e:
        print(f'Ошибка при загрузке {SQUADS_LOCATION}:\n{e}')

    try:
        if os.path.exists(EVENTS_DATA_LOCATION):
            with open(EVENTS_DATA_LOCATION, "r") as f:
                events_json = json.load(f)
            for key, date_str in events_json.items():
                events_data_dict[key] = datetime.fromisoformat(date_str)
    except Exception as e:
        print(f'Ошибка при загрузке {EVENTS_DATA_LOCATION}:\n{e}')

    return Data(users=users_dict, squads=squads_dict, events_data=events_data_dict)

def save(data: Data) -> bool:
    if not os.path.isdir(TEST_DIR if TEST else MAIN_DIR):
        os.mkdir(TEST_DIR if TEST else MAIN_DIR)
    if data.users:
        users_json_serializable = {
            str(user_id): user_info.to_json_serializable()
            for user_id, user_info in data.users.items()
        }
        try:
            with open(USERS_LOCATION, "w") as f:
                json.dump(users_json_serializable, f, indent=4, default=str)
        except IOError as e:
            print(f"Ошибка при сохранении {USERS_LOCATION}:\n{e}")
            return False

    if data.squads:
        for squad in data.squads.values():
            squad.members = [m for m in squad.members if m.user_id in data.users]
        squads_json_serializable = {
            uuid: squad.to_json_serializable()
            for uuid, squad in data.squads.items()
        }
        try:
            with open(SQUADS_LOCATION, "w") as f:
                json.dump(squads_json_serializable, f, indent=4, default=str)
        except IOError as e:
            print(f"Ошибка при сохранении {SQUADS_LOCATION}:\n{e}")
            return False

    if data.events_data:
        events_json_serializable = {
            key: dt.isoformat()
            for key, dt in data.events_data.items()
        }
        try:
            with open(EVENTS_DATA_LOCATION, "w") as f:
                json.dump(events_json_serializable, f, indent=4)
        except IOError as e:
            print(f"Ошибка при сохранении {EVENTS_DATA_LOCATION}:\n{e}")
            return False

    return True
