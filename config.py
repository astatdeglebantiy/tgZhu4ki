# --- imports ---

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from classes import Squad, UserInfo


# --- global variables ---

TEST: bool = os.getenv('TEST', 'true').lower() == 'true'


API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN_MAIN = os.getenv('BOT_TOKEN_MAIN', '')
BOT_TOKEN_TEST = os.getenv('BOT_TOKEN_TEST', '')

# --- paths ---

MAIN_DIR = Path('data')
TEST_DIR = Path('testdata')

BASE_DIR = TEST_DIR if TEST else MAIN_DIR
USERS_LOCATION = BASE_DIR / 'users.json'
SQUADS_LOCATION = BASE_DIR / 'squads.json'
EVENTS_DATA_LOCATION = BASE_DIR / 'events_data.json'


# --- classes ---

@dataclass
class Data:
    users: dict[int, UserInfo] | None = None
    squads: dict[str, Squad] | None = None
    events_data: dict[str, datetime] | None = None


# --- internals ---

def _ensure_base_dir() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise TypeError(f'{path} must contain a JSON object')
    return payload


def _atomic_write(path: Path, payload: dict) -> None:
    _ensure_base_dir()
    temp_path = path.with_suffix(path.suffix + '.tmp')
    with temp_path.open('w', encoding='utf-8') as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)
    os.replace(temp_path, path)


# --- load & save ---

def load() -> Data:
    users_dict: dict[int, UserInfo] = {}
    squads_dict: dict[str, Squad] = {}
    events_data_dict: dict[str, datetime] = {}

    try:
        users_json = _read_json(USERS_LOCATION)
        for user_id_str, user_info_dict in users_json.items():
            users_dict[int(user_id_str)] = UserInfo.from_json_serializable(user_info_dict)
    except Exception as e:
        print(f'Ошибка при загрузке {USERS_LOCATION}:\n{e}')

    try:
        squads_json = _read_json(SQUADS_LOCATION)
        for squad_uuid, squad_dict in squads_json.items():
            squads_dict[squad_uuid] = Squad.from_json_serializable(squad_dict)
    except Exception as e:
        print(f'Ошибка при загрузке {SQUADS_LOCATION}:\n{e}')

    try:
        events_json = _read_json(EVENTS_DATA_LOCATION)
        for key, date_str in events_json.items():
            events_data_dict[key] = datetime.fromisoformat(date_str)
    except Exception as e:
        print(f'Ошибка при загрузке {EVENTS_DATA_LOCATION}:\n{e}')

    return Data(users=users_dict, squads=squads_dict, events_data=events_data_dict)


def save(data: Data) -> bool:
    users = data.users if data.users is not None else {}
    squads = data.squads if data.squads is not None else {}
    events_data = data.events_data if data.events_data is not None else {}

    users_json_serializable = {
        str(user_id): user_info.to_json_serializable()
        for user_id, user_info in users.items()
    }

    for squad in squads.values():
        squad.members = [member for member in squad.members if member.user_id in users]

    squads_json_serializable = {
        uuid: squad.to_json_serializable()
        for uuid, squad in squads.items()
    }

    events_json_serializable = {
        key: dt.isoformat()
        for key, dt in events_data.items()
    }

    try:
        _atomic_write(USERS_LOCATION, users_json_serializable)
        _atomic_write(SQUADS_LOCATION, squads_json_serializable)
        _atomic_write(EVENTS_DATA_LOCATION, events_json_serializable)
    except OSError as e:
        print(f'Ошибка при сохранении данных:\n{e}')
        return False

    return True
