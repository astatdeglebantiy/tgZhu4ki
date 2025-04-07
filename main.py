# --- imports ---

import asyncio
import config
import events
import pyrogram
import uuid
from classes import Status, UserInfo, Squad, SquadMemberStatus, SquadMember
from datetime import datetime
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, \
    InputTextMessageContent


# --- global variables ---

users: dict[int, UserInfo] = {}
squads: dict[str, Squad] = {}
squad_statuses = {
    "Владелец": SquadMemberStatus(can_rename=True, can_kick=True, can_answer_to_join_requests=True),
    "Заместитель": SquadMemberStatus(can_rename=True, can_kick=True, can_answer_to_join_requests=True),
    "Приглядывающий": SquadMemberStatus(can_rename=False, can_kick=True, can_answer_to_join_requests=False),
    "Участник": SquadMemberStatus(can_rename=False, can_kick=False, can_answer_to_join_requests=False)
}
events_data = {}
status: Status = Status()


# --- small main global functions ---

def bug_declination(n) -> str:
    if 11 <= n % 100 <= 14:
        return f"Жуков"
    elif n % 10 == 1:
        return f"Жук"
    elif 2 <= n % 10 <= 4:
        return f"Жука"
    else:
        return f"Жуков"


# --- pyrogram initialization ---

app = pyrogram.Client("zhuki_whatsapp" if not config.TEST else "zhuki_whatsapp_test", api_id=config.API_ID, api_hash=config.API_HASH,
                      bot_token=config.BOT_TOKEN_TEST if config.TEST else config.BOT_TOKEN_MAIN)


# --- small pyrogram global functions ---

async def is_user_in_users(filter, client, message_or_query) -> bool:
    if from_user := getattr(message_or_query, 'from_user', None):
        if user_id := getattr(from_user, 'id', None):
            if user_id in users.keys():
                return True
    return False

async def is_username(filter, client, message_or_query) -> bool:
    if from_user := getattr(message_or_query, 'from_user', None):
        if getattr(from_user, 'username', None):
            return True
    return False

async def start_event(filter, client, message_or_query) -> bool:
    if from_user := getattr(message_or_query, 'from_user', None):
        if username := getattr(from_user, 'username', None):
            if username == 'falseastat':
                if text := getattr(message_or_query, 'text'):
                    if type(text) == pyrogram.types.messages_and_media.message.Str:
                        if text.startswith('e'):
                            return True
    return False

async def awaited_for_reply(filter, client, message) -> bool:
    if from_user := getattr(message, 'from_user', None):
        if user_id := getattr(from_user, 'id', None):
            if user_id in users.keys():
                user_info = users[user_id]
                if user_info.awaited_for_reply:
                    return True
    return False

async def get_user_username(user_id: int):
    user = await app.get_users(user_id)
    return getattr(user, 'username')

async def get_leaderboard():
    sorted_users = sorted(users.items(), key=lambda item: item[1].bug_counts, reverse=True)
    top_10 = sorted_users[:10]
    leaderboard = "Лидерборд по кинутых в Вас Жуков 🪲🪲🪲🪲:\n\n"
    for rank, (user_id, user_info) in enumerate(top_10, start=1):
        username = await get_user_username(user_id)
        bug_count = user_info.bug_counts
        leaderboard += f"  {rank}. {username}: ×{bug_count} {bug_declination(bug_count)}🪲\n"
    return leaderboard


# --- pyrogram commands ---

@app.on_message(pyrogram.filters.command("subscribe") & pyrogram.filters.private)
async def subscribe_command(client, message):
    user_id = message.from_user.id
    if user_id not in users.keys():
        users[user_id] = UserInfo()
        config.save(config.Data(users))
    await set_commands()
    await message.reply_text(
        "У ВАС В БОБОФОНЕ СИКАРАШКИ🪲🪲🪲🪲😱😱😱 ВЫКИНТЕ СВОЙ БОБОФОН И ЗВОНИТЕ АЛМАЗНЫМ ГОЛУБЯМ 💎💎🕊️БОБИНЬ ЛОБОТОМИНЬ 🔮🫘🫘🫘")

@app.on_message((~pyrogram.filters.create(is_user_in_users)) & pyrogram.filters.private)
async def is_not_user_in_users_message(client, message):
    await message.reply_text("ВАС НЕТУ В ЖУЧКАХ😱😱😱🪲🪲\n\nНапишите команду `/subscribe` чтобы зарегистрироваться.")

@app.on_callback_query(~pyrogram.filters.create(is_user_in_users))
async def is_not_user_in_users_callback_query(client, callback_query):
    callback_query.answer("ВАС НЕТУ В ЖУЧКАХ😱😱😱🪲🪲\n\nНапишите команду /subscribe в личных сообщениях бота чтобы зарегистрироваться.")

@app.on_inline_query(~pyrogram.filters.create(is_user_in_users))
async def is_not_user_in_users_inline_query(client, inline_query):
    result = InlineQueryResultArticle(
        title='ВАС НЕТУ В ЖУЧКАХ😱😱😱🪲🪲',
        input_message_content=InputTextMessageContent(
            message_text='ВАС НЕТУ В ЖУЧКАХ😱😱😱🪲🪲\n\nНапишите команду `/subscribe` в личных сообщениях бота чтобы зарегистрироваться.',
        )
    )
    await inline_query.answer([result])

@app.on_message((~pyrogram.filters.create(is_username)) & pyrogram.filters.private)
async def is_not_username_message(client, message):
    await message.reply_text("У ВАС НЕТУ УЗЕРНЭЙМА😱😱😱🪲🪲")

@app.on_message((~pyrogram.filters.create(is_username)) & pyrogram.filters.private)
async def is_not_username_callback_query(client, callback_query):
    await callback_query.answer("У ВАС НЕТУ УЗЕРНЭЙМА😱😱😱🪲🪲")

@app.on_inline_query(~pyrogram.filters.create(is_username))
async def is_not_username_inline_query(client, inline_query):
    result = InlineQueryResultArticle(
        title='У ВАС НЕТУ УЗЕРНЭЙМА😱😱😱🪲🪲',
        input_message_content=InputTextMessageContent(
            message_text='У ВАС НЕТУ УЗЕРНЭЙМА😱😱😱🪲🪲',
            parse_mode=pyrogram.enums.ParseMode.HTML
        )
    )
    await inline_query.answer([result])

@app.on_message(pyrogram.filters.command("unsubscribe") & pyrogram.filters.private)
async def unsubscribe_command(client, message):
    user_id = message.from_user.id
    if user_id in users.keys():
        del users[user_id]
        config.save(config.Data(users))
        await message.reply_text(
            "У ВАС В БОБОФОНЕ БОЛЬШЕ НЕТ СИКАРАШК🪲🪲🪲🪲😱😱😱 БОБИНЬ ЛОБОТОМИНЬ 🔮🫘🫘🫘")

@app.on_message(pyrogram.filters.command("bug_count") & pyrogram.filters.private)
async def bug_count_command(client, message):
    user_id = message.from_user.id
    user_info = users.get(user_id)
    await message.reply_text(f"Кинутые в Вас Жуки🪲(×{user_info.bug_counts})")

@app.on_message(pyrogram.filters.command("leaderboard") & pyrogram.filters.private)
async def leaderboard_command(client, message):
    await message.reply_text(await get_leaderboard())

@app.on_message(pyrogram.filters.command("create_squad") & pyrogram.filters.private)
async def create_squad_command(client, message):
    user_id = message.from_user.id
    user_info = users.get(user_id)
    if user_info.squad_uuid:
        await message.reply_text("Вы уже состоите в скваде")
        return
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        squad_name = args[1]
    else:
        squad_name = f"Сквад @{message.from_user.username}"
    while True:
        squad_uuid = str(uuid.uuid4())[:8]
        if squad_uuid not in squads.keys():
            break
    squads[squad_uuid] = Squad(squad_name, user_id, [SquadMember(user_id, squad_statuses['Владелец'])])
    user_info.squad_uuid = squad_uuid
    config.save(config.Data(users, squads))
    await message.reply_text("Сквад успешно создан!")
    await manage_squad_command(client, message)

@app.on_message(pyrogram.filters.command('manage_squad') & pyrogram.filters.private)
async def manage_squad_command(client, message):
    user_id = message.from_user.id
    user_info = users.get(user_id)
    if not user_info.squad_uuid:
        await message.reply_text("Вы не состоите в скваде")
        return
    keyboard = [
        [InlineKeyboardButton("Информация о скваде", callback_data="squad_manage:info")]
    ]
    if user_id == squads[user_info.squad_uuid].owner_id:
        keyboard.append([InlineKeyboardButton("Изменить название", callback_data="squad_manage:change_name")])
    keyboard.append([InlineKeyboardButton("Выйти из сквада", callback_data="squad_manage:leave")])
    await message.reply_text("**Управление сквадом**", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_message(pyrogram.filters.command('join_squad') & pyrogram.filters.private)
async def join_squad_command(client, message):
    user_id = message.from_user.id
    user_info = users.get(user_id)
    if user_info.join_squad_pending:
        keyboard = [
            [InlineKeyboardButton('Отменить заявку', callback_data='cancel_squad_join_application')]
        ]
        message.reply_text('Вы уже подали заявку на вступление', reply_markup=InlineKeyboardMarkup(keyboard))
    if user_info.squad_uuid:
        await message.reply_text("Вы уже состоите в скваде")
        return
    args = message.text.split(maxsplit=1)
    if len(args) == 2:
        squad_uuid = args[1]
    else:
        await message.reply_text("Неверный ввод команды! Используйте по этому примеру:\n\n`/join_squad abcde123`")
        return
    if squad_uuid not in squads.keys():
        await message.reply_text("Сквад с указанным айди не найден")
        return
    user_info.join_squad_pending = squad_uuid
    squad = squads[squad_uuid]
    keyboard = [
        [
            InlineKeyboardButton("Принять", callback_data=f"squad:accept:{squad_uuid}:{user_id}"),
            InlineKeyboardButton("Отклонить", callback_data=f"squad:decline:{squad_uuid}:{user_id}")
        ]
    ]
    try:
        await client.send_message(
            chat_id=squad.owner_id,
            text=(
                f"Поступила заявка на вступление в сквад <b>{squad.name}</b> "
                f"от пользователя @{message.from_user.username}.\n\n"
                "Нажмите «Принять» для одобрения или «Отклонить» для отказа."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=pyrogram.enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text("Не удалось отправить уведомление капитану. Попробуйте позже")
        return
    config.save(config.Data(users, squads))
    await message.reply_text("Ваша заявка отправлена капитану сквада. Ожидайте решения...")

@app.on_callback_query(pyrogram.filters.regex(r"^squad:(accept|decline):"))
async def squad_join_application_answer(client, callback_query):
    _data = callback_query.data.split(":")
    if len(_data) != 4:
        await callback_query.answer("Неверные данные запроса")
        return
    action, squad_uuid, applicant_id_str = _data[1], _data[2], _data[3]
    applicant_id = int(applicant_id_str)
    user_id = callback_query.from_user.id
    squad = squads.get(squad_uuid)
    if not squad:
        await callback_query.answer("Сквад не найден")
        return
    fact_check_status = False
    for member in squad.members:
        if member.user_id == user_id:
            if member.status.can_answer_to_join_requests is True:
                fact_check_status = True
                break
            else:
                await callback_query.answer("У вас нет полномочий для обработки этой заявки")
                return
    if not fact_check_status:
        return
    applicant_info = users.get(applicant_id)
    if not applicant_info:
        await callback_query.anwer("Пользователь не найден")
        return
    if applicant_info.join_squad_pending != squad_uuid:
        await callback_query.answer("Заявка уже обработана или не найдена")
        print(applicant_info.join_squad_pending)
        print(squad_uuid)
        return
    if action == 'accept':
        squad.members.append(SquadMember(applicant_id, squad_statuses['Участник']))
        applicant_info.squad_uuid = squad_uuid
        applicant_info.join_squad_pending = None
        await callback_query.answer("Заявка принята!")
        try:
            await client.send_message(
                chat_id=applicant_id,
                text=f"Ваша заявка на вступление в сквад <b>{squad.name}</b> принята!",
                parse_mode=pyrogram.enums.ParseMode.HTML
            )
        except Exception as e:
            print(f"Ошибка уведомления заявителя: {e}")
    elif action == 'decline':
        applicant_info.join_squad_pending = None
        await callback_query.answer("Заявка отклонена")
        try:
            await client.send_message(
                chat_id=applicant_id,
                text=f"Ваша заявка на вступление в сквад <b>{squad.name}</b> отклонена.",
                parse_mode=pyrogram.enums.ParseMode.HTML
            )
        except Exception as e:
            print(f"Ошибка уведомления заявителя: {e}")

    config.save(config.Data(users, squads))

@app.on_callback_query(pyrogram.filters.regex(r"^squad_manage:"))
async def squad_manage_callback_query(client, callback_query):
    _data = callback_query.data
    action = _data.split(":", 1)[1]
    user_id = callback_query.from_user.id
    user_info = users[user_id]
    if not user_info.squad_uuid:
        await callback_query.answer("Вы не состоите в скваде")
        return
    squad_uuid = user_info.squad_uuid
    squad = squads[user_info.squad_uuid]
    if not squad:
        await callback_query.answer("Информация о скваде не найдена.", show_alert=True)
        return

    match action:
        case 'info':
            info_message = (
                f"Сквад: {squad.name}\n"
                f"Код сквада: <code>{squad_uuid}</code>\n"
                f"Владелец: @{await get_user_username(squad.owner_id)}\n\n"
                "Участники:\n"
            )
            for member in squad.members:
                info_message += f" - @{await get_user_username(member.user_id)}\n"
            await callback_query.message.reply_text(info_message, parse_mode=pyrogram.enums.ParseMode.HTML)
        case 'change_name':
            if squad.owner_id != user_id:
                await callback_query.answer("Вы не капитан!")
                return
            user_info.awaited_for_reply = 'squad_manage:change_name'
            await callback_query.message.reply_text("Введите новое название сквада:")
            await callback_query.answer()
        case 'leave':
            if squad.owner_id == user_id:
                for member in squad.members:
                    member_info = users[member.user_id]
                    member_info.squad_uuid = None
                del squads[squad_uuid]
                await callback_query.answer("Вы покинули сквад. Сквад распущен.", show_alert=True)
            else:
                for member in squad.members:
                    if member.user_id == user_id:
                        squad.members.remove(member)
                user_info.squad_uuid = None
                await callback_query.answer("Вы покинули сквад.", show_alert=True)

@app.on_inline_query()
async def inline_query_handler(client, inline_query):
    text = inline_query.query.strip()
    target_username = text if text.startswith("@") else None
    if not target_username:
        result = InlineQueryResultArticle(
            title=status.inline_nickname_error_title,
            input_message_content=InputTextMessageContent(status.inline_nickname_error_input_message_content),
            description=status.inline_nickname_error_description
        )
        await inline_query.answer([result])
        return
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(status.button_click_to_send_text,
                                                           callback_data=f"send_bug:{target_username}")]])
    result = InlineQueryResultArticle(
        title=status.inline_title,
        input_message_content=InputTextMessageContent(
            message_text=(status.inline_input_message_content(target_username.replace('@', ''))),
            parse_mode=pyrogram.enums.ParseMode.HTML
        ),
        reply_markup=keyboard,
        description=status.inline_description(target_username.replace('@', ''))
    )
    await inline_query.answer([result])

send_bug_lock = asyncio.Lock()
@app.on_callback_query(pyrogram.filters.regex(r"^send_bug:"))
async def send_bug_callback_query(client, callback_query):
    async with send_bug_lock:
        user_id = callback_query.from_user.id
        data_parts = callback_query.data.split(":")
        if len(data_parts) != 2:
            await callback_query.answer("Неверный формат данных", show_alert=True)
            return
        _, target_username = data_parts
        try:
            target_user = await client.get_users(target_username)
        except Exception:
            await callback_query.answer("БЕШАСТИ ❗️❗️❗️ Не удалось найти пользователя.", show_alert=True)
            return
        if target_user.id == user_id:
            await callback_query.answer("БЕШАСТИ ❗️❗️❗️ СЕЛФХАРМ ❗️❗️❗️ ДОНТ ДУ ИТ", show_alert=True)
            return
        if not getattr(target_user, 'username'):
            await callback_query.answer("БЕШАСТИ ❗️❗️❗️ ТАРГЕТ ДОНТ ХЭВ УСЭРНАМЕ", show_alert=True)
            return
        target_user_info = users.get(target_user.id)
        if not target_user_info:
            await callback_query.answer("БЕШАСТИ ❗️❗️❗️ Пользователя нет в Жуках.", show_alert=True)
            return
        user_info = users[user_id]
        if user_info.last_send_time:
            if (user_info.last_send_time - datetime.now()).total_seconds() < 0:
                time_delta = user_info.last_send_time - datetime.now() + status.window_duration
                total_seconds = int(time_delta.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                await callback_query.answer(
                    status.end_window_error_message(hours=hours, minutes=minutes, seconds=seconds),
                    show_alert=True
                )
                return
        try:
            target_user_info.bug_counts += status.count
            user_info.screen_count += 1
            if user_info.screen_count >= status.rate_limit:
                user_info.last_send_time = datetime.now()
                user_info.screen_count = 0
            config.save(config.Data(users, squads))
            message = status.send_message(callback_query.from_user.username, target_user.username, target_user_info.bug_counts, bug_declination)
            await callback_query.answer(
                message,
                show_alert=True
            )
            if status.send_message_photo:
                await client.send_photo(
                    chat_id=target_user.id,
                    photo=status.send_message_photo,
                    caption=message
                )
            else:
                await client.send_message(chat_id=target_user.id, text=message.replace(f'@{target_user.username}'))
            await app.send_message(chat_id=config.LOGS_CHAT_ID, text=message)
        except Exception as e:
            await callback_query.answer(
                status.error_message(),
                show_alert=True)
            print(str(e))

@app.on_message(pyrogram.filters.create(awaited_for_reply))
async def awaited_for_reply_message(client, message):
    user_id = message.from_user.id
    user_info = users[user_id]
    awaited_message_for_reply = user_info.awaited_for_reply
    print(awaited_message_for_reply)
    if awaited_message_for_reply.startswith('squad_manage:'):
        _data = awaited_message_for_reply.split(":")
        print(_data)
        print(len(_data))
        if len(_data) != 2:
            await message.reply_text("Неверные данные запроса")
            user_info.awaited_for_reply = None
            return
        action = _data[1]
        if action == 'change_name':
            if not user_info.squad_uuid:
                await message.reply_text("Вы не состоите в скваде")
                user_info.awaited_for_reply = None
                return
            squad = squads[user_info.squad_uuid]
            if user_id == squad.owner_id:
                new_name = message.text
                if new_name:
                    squad.name = new_name
                    await message.reply_text(f"Название сквада изменено на {new_name}")
                else:
                    await message.reply_text("Сообщение пустое")
            else:
                await message.reply_text("Вы не владелец сквада")
        else:
            await message.reply_text("Неверные данные запроса")
    else:
        await message.reply_text("Неверные данные запроса")
    user_info.awaited_for_reply = None

@app.on_message(pyrogram.filters.create(start_event))
async def start_event_message(client, message):
    text = message.text
    for task in asyncio.all_tasks():
        if task.get_name().startswith('event:'):
            await message.reply_text('Ивент уже запущен')
            return
    if text == 'e_invasion':
        for user_id in users.keys():
            users[user_id].last_send_time = None
            users[user_id].screen_count = 0
        config.save(config.Data(users))
        await events.invasion_of_bugs.start(status, app)
        await message.reply_text('Успешно (Нашествие Жуков)')
    elif text == 'e_gas':
        for user_id in users.keys():
            users[user_id].last_send_time = None
            users[user_id].screen_count = 0
        config.save(config.Data(users))
        await events.gas_attack.start(status, app)
        await message.reply_text('Успешно (Газовая атака)')
    else:
        await message.reply_text('Неверный ввод')


# --- starting ---

async def set_commands():
    commands = [
        BotCommand("subscribe", "Зарегистрироваться в Жуках🪲🪲🪲"),
        BotCommand("unsubscribe", "!!!ВСЕ ВАШИ ЖУКИ УДАЛЯТСЯ!!! Удалится в Жуках🪲🪲🪲"),
        BotCommand("bug_count", "Количество кинутых в Вас Жуков🪲🪲🪲"),
        BotCommand("leaderboard", "Лидерборды по количеству кинутых в Вас Жуков🪲🪲🪲"),
        BotCommand("create_squad", "Создать сквад 🏴‍☠️🪲"),
        BotCommand("manage_squad", "Управление сквадом 🏴‍☠️⚙️🪲"),
        BotCommand("join_squad", "Зайти в сквад 🏴‍☠️💬🪲"),
    ]
    await app.set_bot_commands(commands)

async def run_pyrogram():
    await app.start()
    await set_commands()
    # asyncio.create_task(event_manager())
    await pyrogram.idle()

if __name__ == "__main__":
    data = config.load()
    users = data.users
    squads = data.squads
    events_data = data.events_data
    print(data.__dict__)
    app.run(run_pyrogram())
