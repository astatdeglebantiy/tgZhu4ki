# --- imports ---

import asyncio

import pyrogram

import broadcast_message
import random
from asyncio import Task
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta

import config


# --- classes ---

class SquadMemberStatus:
    def __init__(self, can_rename: bool, can_kick: bool, can_answer_to_join_requests: bool):
        self.can_rename = can_rename
        self.can_kick = can_kick
        self.can_answer_to_join_requests = can_answer_to_join_requests
    def to_json_serializable(self):
        return {
            'can_rename': self.can_rename,
            'can_kick': self.can_kick,
            'can_answer_to_join_requests': self.can_answer_to_join_requests,
        }
    @classmethod
    def from_json_serializable(cls, _dict: dict):
        can_rename = _dict.get('can_rename')
        if not isinstance(can_rename, bool):
            raise TypeError(f"'can_rename' must be a bool, not {type(can_rename)}")
        can_kick = _dict.get('can_kick')
        if not isinstance(can_kick, bool):
            raise TypeError(f"'can_kick' must be a bool, not {type(can_kick)}")
        can_answer_to_join_requests = _dict.get('can_answer_to_join_requests')
        if not isinstance(can_answer_to_join_requests, bool):
            raise TypeError(f"'can_answer_to_join_requests' must be a bool, not {type(can_answer_to_join_requests)}")
        return cls(can_rename, can_kick, can_answer_to_join_requests)

class UserInfo:
    def __init__(self, last_send_time: datetime | None = None, bug_counts: int = 0, squad_uuid: str | None = None, join_squad_pending: str | None = None,
                 awaited_for_reply: str | None = None, screen_count: int = 0):
        self.last_send_time = last_send_time
        self.bug_counts = bug_counts
        self.squad_uuid = squad_uuid
        self.join_squad_pending = join_squad_pending
        self.awaited_for_reply = awaited_for_reply
        self.screen_count = screen_count
    def to_json_serializable(self):
        return {
            'last_send_time': self.last_send_time.isoformat() if self.last_send_time else None,
            'bug_counts': self.bug_counts,
            'squad_uuid': self.squad_uuid,
            'join_squad_pending': self.join_squad_pending,
            'awaited_for_reply': self.awaited_for_reply,
            'screen_count': self.screen_count,
        }
    @classmethod
    def from_json_serializable(cls, _dict: dict):
        last_send_time_str = _dict.get('last_send_time')
        last_send_time = datetime.fromisoformat(last_send_time_str) if last_send_time_str else None
        bug_counts = _dict.get('bug_counts')
        if not isinstance(bug_counts, int):
            raise TypeError(f"'bug_counts' must be an int, not {type(bug_counts)}")
        squad_uuid = _dict.get('squad_uuid')
        if squad_uuid is not None and not isinstance(squad_uuid, str):
            raise TypeError(f"'squad_uuid' must be a str or None, not {type(squad_uuid)}")
        join_squad_pending = _dict.get('join_squad_pending')
        if join_squad_pending is not None and not isinstance(join_squad_pending, str):
            raise TypeError(f"'join_squad_pending' must be a str or None, not {type(join_squad_pending)}")
        awaited_for_reply = _dict.get('awaited_for_reply')
        if awaited_for_reply is not None and not isinstance(awaited_for_reply, str):
            raise TypeError(f"'awaited_for_reply' must be a str or None, not {type(awaited_for_reply)}")
        screen_count = _dict.get('screen_count')
        if not isinstance(screen_count, int):
            raise TypeError(f"'screen_count' must be an int, not {type(screen_count)}")
        return cls(last_send_time, bug_counts, squad_uuid, join_squad_pending, awaited_for_reply, screen_count)

class SquadMember:
    def __init__(self, user_id: int, status: SquadMemberStatus):
        self.user_id = user_id
        self.status = status
    def to_json_serializable(self):
        return {
            'user_id': self.user_id,
            'status': self.status.to_json_serializable() if self.status else None,
        }
    @classmethod
    def from_json_serializable(cls, _dict: dict):
        user_id = _dict.get('user_id')
        if not isinstance(user_id, int):
            raise TypeError(f"'user_id' must be an int, not {type(user_id)}")
        status_dict = _dict.get('status')
        if not isinstance(status_dict, dict):
            raise TypeError(f"'status' must be a dict, not {type(status_dict)}")
        status = SquadMemberStatus.from_json_serializable(status_dict)
        return cls(user_id, status)

class Squad:
    def __init__(self, name: str, owner_id: int, members: list[SquadMember]):
        self.name = name
        self.owner_id = owner_id
        self.members = members
    def to_json_serializable(self):
        return {
            'name': self.name,
            'owner_id': self.owner_id,
            'members': [member.to_json_serializable() for member in self.members] if self.members else [],
        }
    @classmethod
    def from_json_serializable(cls, _dict: dict):
        name = _dict.get('name')
        if not isinstance(name, str):
            raise TypeError(f"'name' must be a str, not {type(name)}")
        owner_id = _dict.get('owner_id')
        if not isinstance(owner_id, int):
            raise TypeError(f"'owner_id' must be an int, not {type(owner_id)}")
        members_list = _dict.get('members')
        if not isinstance(members_list, list):
            raise TypeError(f"'members' must be a list, not {type(members_list)}")
        members = [SquadMember.from_json_serializable(member_dict) for member_dict in members_list]
        return cls(name, owner_id, members)

class Status:
    """
    Script status
    """
    def __init__(self,
                 rate_limit: int = 1,
                 count: int = 1,
                 window_duration: timedelta = timedelta(hours=3),
                 button_click_to_send_text: str = '🪲🪲🪲',
                 send_message = lambda _from, to, count, bug_declination: random.choice([
                    f'@{_from} кинул(-а) в @{to} Жука🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} подло подкинул(-а) @{to} Жука🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} зашвырнул(-а) Жука🪲(×1) в @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} залепил(-а) в @{to} Жука🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} зафигачил(-а) в @{to} Жука🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} десантировал(-а) Жука🪲(×1) в @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} продемонстрировал(-а) аэродинамические свойства Жука🪲(×1) на @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} проводил(-а) Жука🪲(×1) в последний путь к @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} зафутболил(-а) Жука🪲(×1) в @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} зарядил(-а) Жука🪲(×1) в @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} катапультировал(-а) Жука🪲(×1) в @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} угостил(-а) @{to} Жуком🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} огрел(-а) @{to} Жуком🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} накормил(-а) @{to} Жуком🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} преподнёс(-а) Жука🪲(×1) @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} торжественно вручил(-а) Жука🪲(×1) @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} наградил(-а) @{to} Жуком🪲(×1) (всего ×{count} {bug_declination(count)})',
                    f'@{_from} втюхал(-а) Жука🪲(×1) @{to} (всего ×{count} {bug_declination(count)})',
                    f'@{_from} присунул(-а) @{to} Жука🪲(×1) (всего ×{count} {bug_declination(count)})',
                 ]),
                 send_message_photo: str | None = 'https://imgur.com/e8g8TIm',
                 end_window_error_message = lambda hours, minutes, seconds: f'БЕШАСТИ🔮🔮\nПроцессор Вашего бобофона🫘🫘 перегрелся (100°C)❗️❗️\n\nВы сможете кинуть Жука🪲🪲 снова через {hours} ч. {minutes} мин. {seconds} сек. 🪲🪲',
                 error_message = lambda: 'БЕШАСТИ ❗️❗️❗️ Не удалось кинуть Жук🪲(×1). (Убедитесь, что пользователь начал диалог с ботом)',
                 inline_title: str = 'Кинуть Жука🪲🪲🪲',
                 inline_input_message_content = lambda target_username: f'Нажмите кнопку чтобы кинуть Жука @{target_username}🪲🪲\n\n'
                                                                        f'<a href="t.me/zhuki_whatsapp_bot">Чтобы тоже ловить Жуков нажмите старт в боте</a>',
                 inline_description = lambda target_username: f'Жук для @{target_username}🪲🪲',
                 inline_nickname_error_title: str = 'БЕШАСТИ🔮, не удалось кинуть Жука🪲🪲',
                 inline_nickname_error_description: str = 'Напишите никнейм @НИКНЕЙМ ❗️❗️❗️',
                 inline_nickname_error_input_message_content: str = 'БЕШАСТИ🔮🔮🧿🧿🧿🧿🪬🪬🪬, не удалось кинуть Жука🪲🪲\nНапишите никнейм @НИКНЕЙМ ❗️❗️❗️',
    ):
        self.rate_limit = rate_limit
        self.count = count
        self.window_duration = window_duration
        self.button_click_to_send_text = button_click_to_send_text
        self.send_message = send_message
        self.send_message_photo = send_message_photo
        self.end_window_error_message = end_window_error_message
        self.error_message = error_message
        self.inline_title = inline_title
        self.inline_input_message_content = inline_input_message_content
        self.inline_description = inline_description
        self.inline_nickname_error_title = inline_nickname_error_title
        self.inline_nickname_error_description = inline_nickname_error_description
        self.inline_nickname_error_input_message_content = inline_nickname_error_input_message_content
    def update(self, other: "Status"):
        for attr, value in vars(other).items():
            setattr(self, attr, value)
    """def to_json_serializable(self):
        return {
            'rate_limit': self.rate_limit,
            'window_duration': self.window_duration,
        }
    @classmethod
    def from_json_serializable(cls, _dict: dict):
        rate_limit = _dict.get('rate_limit')
        if not isinstance(rate_limit, int):
            raise TypeError(f"'rate_limit' must be an int, not {type(rate_limit)}")
        window_duration = _dict.get('window_duration')
        if not isinstance(window_duration, (int, float)):
            raise TypeError(f"'window_duration' must be an int or float, not {type(window_duration)}")
        return cls(rate_limit, window_duration)"""

class Event:
    """
    Event with coroutine base
    """
    def __init__(self, name: str, coro: Callable[..., Coroutine], new_status: Status = Status(), duration: float = 3600):
        self.name = name
        self.coro = coro
        self.new_status = new_status
        self.duration = duration
    async def start(self, status: Status) -> Task:
        async def task():
            status.error_message = self.new_status.error_message
            status.send_message_photo = self.new_status.send_message_photo
            status.end_window_error_message = self.new_status.end_window_error_message
            status.send_message = self.new_status.send_message
            status.rate_limit = self.new_status.rate_limit
            status.window_duration = self.new_status.window_duration
            answer = await self.coro(self.duration)
            status.error_message = Status().error_message
            status.send_message_photo = Status().send_message_photo
            status.end_window_error_message = Status().end_window_error_message
            status.send_message = Status().send_message
            status.rate_limit = Status().rate_limit
            status.window_duration = Status().window_duration
            return answer
        return asyncio.create_task(coro=task(), name=f'event:{self.name}')

class BasicEvent:
    """
    Just basic event
    """
    def __init__(self, name: str, new_status: Status = Status(), duration: float = 3600,
                 start_message: str | None = None, end_message: str | None = None,
                 start_message_photo: str | None = None, end_message_photo: str | None = None):
        self.name = name
        self.new_status = new_status
        self.duration = duration
        self.start_message = start_message
        self.end_message = end_message
        self.start_message_photo = start_message_photo
        self.end_message_photo = end_message_photo
    async def start(self, status: Status, app: pyrogram.Client) -> Task:
        async def task():
            status.update(self.new_status)
            if self.start_message:
                if self.start_message_photo:
                    await broadcast_message.broadcast_message(app, self.start_message, self.start_message_photo)
                else:
                    await broadcast_message.broadcast_message(app, self.start_message)
            await asyncio.sleep(self.duration)
            if self.end_message:
                if self.end_message_photo:
                    await broadcast_message.broadcast_message(app, self.end_message, self.end_message_photo)
                else:
                    await broadcast_message.broadcast_message(app, self.end_message)
            status.update(Status())
            return True
        return asyncio.create_task(coro=task(), name=f'event:{self.name}')
