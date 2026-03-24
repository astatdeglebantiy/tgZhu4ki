from __future__ import annotations

import asyncio
import logging
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import config
from classes import Squad, SquadMember, SquadMemberStatus, UserInfo


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

users: dict[int, UserInfo] = {}
squads: dict[str, Squad] = {}

squad_statuses = {
    'Владелец': SquadMemberStatus(can_rename=True, can_kick=True, can_answer_to_join_requests=True),
    'Заместитель': SquadMemberStatus(can_rename=True, can_kick=True, can_answer_to_join_requests=True),
    'Приглядывающий': SquadMemberStatus(can_rename=False, can_kick=True, can_answer_to_join_requests=False),
    'Участник': SquadMemberStatus(can_rename=False, can_kick=False, can_answer_to_join_requests=False),
}


@dataclass
class RuntimeStatus:
    rate_limit: int = 1


runtime_status = RuntimeStatus()
throw_counters: dict[tuple[int, int], int] = defaultdict(int)


def load_state() -> None:
    global users, squads
    data = config.load()
    users = data.users or {}
    squads = data.squads or {}


def save_state() -> None:
    config.save(config.Data(users=users, squads=squads))


def bug_declination(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return 'Жуков'
    if n % 10 == 1:
        return 'Жук'
    if 2 <= n % 10 <= 4:
        return 'Жука'
    return 'Жуков'


def parse_username(text: str) -> str | None:
    match = re.search(r'@([A-Za-z0-9_]{5,32})', text)
    if not match:
        return None
    return match.group(1)


async def ensure_registered(message: Message) -> UserInfo | None:
    if not message.from_user:
        return None
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer('Вы не зарегистрированы. Используйте /subscribe')
        return None
    return users[user_id]


@router.message(Command('start'))
async def start_cmd(message: Message) -> None:
    await message.answer('Привет! Это обновлённый бот на aiogram. Используй /subscribe чтобы начать.')


@router.message(Command('subscribe'))
async def subscribe_cmd(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    users.setdefault(user_id, UserInfo())
    save_state()
    await message.answer('Регистрация успешна 🪲')


@router.message(Command('unsubscribe'))
async def unsubscribe_cmd(message: Message) -> None:
    if not message.from_user:
        return
    removed = users.pop(message.from_user.id, None)
    if removed and removed.squad_uuid and removed.squad_uuid in squads:
        squad = squads[removed.squad_uuid]
        squad.members = [m for m in squad.members if m.user_id != message.from_user.id]
    save_state()
    await message.answer('Вы отписаны.')


@router.message(Command('bug_count'))
async def bug_count_cmd(message: Message) -> None:
    user_info = await ensure_registered(message)
    if not user_info:
        return
    count = user_info.bug_counts
    await message.answer(f'Кинутые в Вас Жуки: ×{count} {bug_declination(count)}')


@router.message(Command('leaderboard'))
async def leaderboard_cmd(message: Message) -> None:
    if not users:
        await message.answer('Пока нет пользователей в рейтинге.')
        return
    rating = sorted(users.items(), key=lambda item: item[1].bug_counts, reverse=True)[:10]
    lines = ['Лидерборд по жукам:']
    for index, (uid, info) in enumerate(rating, start=1):
        lines.append(f'{index}. user_id={uid}: ×{info.bug_counts}')
    await message.answer('\n'.join(lines))


@router.message(Command('throw'))
async def throw_bug_cmd(message: Message, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    from_user = message.from_user
    sender_info = await ensure_registered(message)
    if not sender_info:
        return

    username = parse_username(message.text)
    if not username:
        await message.answer('Использование: /throw @username')
        return

    try:
        target_chat = await bot.get_chat(f'@{username}')
    except Exception:
        await message.answer('Не удалось найти пользователя по username.')
        return

    if not target_chat.id or target_chat.id not in users:
        await message.answer('Цель не зарегистрирована в боте.')
        return

    target_info = users[target_chat.id]
    key = (from_user.id, target_chat.id)
    if throw_counters[key] >= runtime_status.rate_limit:
        await message.answer('Лимит бросков исчерпан, попробуйте позже.')
        return

    throw_counters[key] += 1
    target_info.bug_counts += 1
    save_state()

    await message.answer(
        f'@{from_user.username or from_user.id} кинул в @{username} Жука 🪲 '
        f'(всего у цели ×{target_info.bug_counts} {bug_declination(target_info.bug_counts)})'
    )


@router.message(Command('create_squad'))
async def create_squad_cmd(message: Message) -> None:
    if not message.from_user:
        return
    user_info = await ensure_registered(message)
    if not user_info:
        return
    if user_info.squad_uuid:
        await message.answer('Вы уже состоите в скваде.')
        return

    name = message.text.split(maxsplit=1)[1] if message.text and len(message.text.split(maxsplit=1)) == 2 else f'Сквад @{message.from_user.username or message.from_user.id}'

    squad_uuid = str(uuid.uuid4())[:8]
    squads[squad_uuid] = Squad(name, message.from_user.id, [SquadMember(message.from_user.id, squad_statuses['Владелец'])])
    user_info.squad_uuid = squad_uuid
    save_state()

    await message.answer(f'Сквад создан: {name}\nID: {squad_uuid}')


@router.message(Command('join_squad'))
async def join_squad_cmd(message: Message) -> None:
    if not message.from_user:
        return
    user_info = await ensure_registered(message)
    if not user_info:
        return
    if user_info.squad_uuid:
        await message.answer('Вы уже в скваде.')
        return

    parts = message.text.split(maxsplit=1) if message.text else []
    if len(parts) != 2:
        await message.answer('Использование: /join_squad <squad_id>')
        return

    squad_id = parts[1].strip()
    squad = squads.get(squad_id)
    if not squad:
        await message.answer('Сквад не найден.')
        return

    squad.members.append(SquadMember(message.from_user.id, squad_statuses['Участник']))
    user_info.squad_uuid = squad_id
    save_state()
    await message.answer(f'Вы вступили в сквад {squad.name}')


@router.message(Command('my_squad'))
async def my_squad_cmd(message: Message) -> None:
    if not message.from_user:
        return
    user_info = await ensure_registered(message)
    if not user_info:
        return
    if not user_info.squad_uuid or user_info.squad_uuid not in squads:
        await message.answer('Вы не состоите в скваде.')
        return

    squad = squads[user_info.squad_uuid]
    await message.answer(
        f'<b>{squad.name}</b>\nID: <code>{user_info.squad_uuid}</code>\nУчастников: {len(squad.members)}',
        parse_mode=ParseMode.HTML,
    )


@router.message(F.text)
async def fallback(message: Message) -> None:
    await message.answer('Команда не распознана. Доступно: /subscribe /throw /leaderboard /create_squad /join_squad /my_squad')


async def main() -> None:
    if not (config.API_ID and config.API_HASH and (config.BOT_TOKEN_TEST or config.BOT_TOKEN_MAIN)):
        raise RuntimeError('Set API_ID, API_HASH and BOT_TOKEN_TEST/BOT_TOKEN_MAIN environment variables.')

    load_state()
    token = config.BOT_TOKEN_TEST if config.TEST else config.BOT_TOKEN_MAIN
    bot = Bot(token=token, parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    logger.info('Bot started with aiogram')
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
