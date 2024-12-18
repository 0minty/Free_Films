from library import *

bot = Bot(token, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()


class StateFilm(StatesGroup):
    film_cal = State()


class StateSerial(StatesGroup):
    serial_cal = State()


class StateRec(StatesGroup):
    recc_cal = State()


url_sub_channel = 'https://t.me/LuizianaFilms'


async def check_sub_channel(state, message, user_id):
    data = await state.get_data()
    mes = data.get('mes_id')
    kb = [
        [types.InlineKeyboardButton(text='↗️Подписаться', url=url_sub_channel)],
        [types.InlineKeyboardButton(text='🔄Проверить подписку', callback_data='check_sub')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    sub_stat = await bot.get_chat_member(chat_id=chan, user_id=user_id)
    if sub_stat.status in ['member', 'administrator', 'creator']:
        return True
    else:
        try:
            data = await state.get_data()
            mes = data.get('mes_id')
            mes = await bot.edit_message_text(chat_id=message.chat.id, message_id=mes.message_id,
                                              text='❗️Вы не подписались на наш канал!', reply_markup=keyboard)
            await state.update_data(mes_id=mes)
        except Exception as e:
            mes = await bot.edit_message_text(chat_id=message.chat.id, message_id=mes.message_id,
                                              text='❗️Вы не подписались на наш канал!', reply_markup=keyboard)
            await state.update_data(mes_id=mes)
        return False


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    result = await check_user_id(user_id)
    await state.set_state()
    sub_stat = await bot.get_chat_member(chat_id=chan, user_id=user_id)
    if sub_stat.status in ['member', 'administrator', 'creator']:
        if result:
            kb = [
                [types.InlineKeyboardButton(text='🎥Фильм/🍿Сериал', callback_data='film')],
                [types.InlineKeyboardButton(text='🌟Не знаешь, что посмотреть? Кликай!', callback_data='recommends')]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
            mes_id = await bot.send_message(message.chat.id, text='👋Привет, что будем смотреть?',
                                            reply_markup=keyboard)
            await state.update_data(mes_id=mes_id)
        else:
            await start_base(user_id)
            # await bot.send_message(ID_ADM, f'Новый пользователь: {user_id}\nUserName: @{user_name}')
            kb = [
                [types.InlineKeyboardButton(text='🎥Фильм/🍿Сериал', callback_data='film')],
                [types.InlineKeyboardButton(text='🌟Не знаешь, что посмотреть? Кликай!', callback_data='recommends')]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
            mes_id = await bot.send_message(message.chat.id, text='👋Привет, что будем смотреть?',
                                            reply_markup=keyboard)
            await state.update_data(mes_id=mes_id)
    else:
        kb = [
            [types.InlineKeyboardButton(text='↗️Подписаться', url='https://t.me/LuizianaFilms')],
            [types.InlineKeyboardButton(text='🔄Проверить подписку', callback_data='check_sub')]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes_id = await message.answer('❗️Вы должны подписаться на наш канал',
                                      reply_markup=keyboard)
        await state.update_data(mes_id=mes_id)


@dp.callback_query(F.data == 'check_sub')
async def hand_check_sub(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = data.get('mes_id')
    kb = [
        [types.InlineKeyboardButton(text='↗️Подписаться', url='https://t.me/LuizianaFilms')],
        [types.InlineKeyboardButton(text='🔄Проверить подписку', callback_data='check_sub')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    sub_stat = await bot.get_chat_member(chat_id=chan, user_id=callback.from_user.id)
    if sub_stat.status in ['member', 'administrator', 'creator']:
        kb = [
            [types.InlineKeyboardButton(text='◀️', callback_data='back')]
        ]
        keyboard_approve = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes_id = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                             text='✅Спасибо за подписку!', reply_markup=keyboard_approve)
        await state.update_data(mes_id=mes_id)
    else:
        try:
            data = await state.get_data()
            mes = data.get('mes_id')
            await bot.delete_message(callback.message.chat.id, mes.message_id)
            mes_id = await callback.message.answer('❗️Вы не подписались на наш канал!',
                                                   reply_markup=keyboard)
            await state.update_data(mes_id=mes_id)
        except Exception as e:
            await bot.delete_message(callback.message.chat.id, mes.message_id)
            mes = await callback.message.answer('❗️Вы не подписались на наш канал!', reply_markup=keyboard)
            await state.update_data(mes_id=mes)


@dp.message(Command('us'))
async def adm_user(message: types.Message):
    user_id = message.from_user.id
    if user_id in ID_ADM:
        async with aiosqlite.connect('base.db') as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT COUNT(user_id) FROM users')
            result = await cursor.fetchone()
            count = result[0]
            await bot.send_message(message.chat.id, f'Кол-во пользователей: {count}')


@dp.callback_query(F.data == 'film')
async def film_search(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    a = await check_sub_channel(state, callback.message, user_id=user_id)
    if a:
        data = await state.get_data()
        mes = data.get('mes_id')
        kb = [
            [types.InlineKeyboardButton(text='◀️', callback_data="back")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes_id = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                             text='🎥Введи название фильма или сериала:', reply_markup=keyboard)
        await state.update_data(mes_id=mes_id)
        await state.set_state(StateFilm.film_cal)


@dp.message(StateFilm.film_cal)
async def film_handler(message: types.Message, state: FSMContext):
    web = 'www.kinopoisk.cx'
    film = message.text
    data = await state.get_data()
    mes = data.get('mes_id')
    kb = [
        [types.InlineKeyboardButton(text='◀️', callback_data="back")]
    ]
    keyboard_d = types.InlineKeyboardMarkup(inline_keyboard=kb)
    result = await get_Films(film)
    if result is not None:
        url_it, clear_b, results, name_film = result
        kb = []
        for i, result in enumerate(results):
            if i >= 5:
                break
            title = result.find('p', class_='name').find('a').text
            title_name = result.find('p', class_='name').text
            link = result.find('p', class_='name').find('a')['href']
            if title[-7:-1] == 'фильм':
                link = link.replace('film', 'series')
            url_more = web + link
            kb.append([types.InlineKeyboardButton(text=f'🎥{title_name}', url=f'{url_more}')])
        kb.append([types.InlineKeyboardButton(text='◀️', callback_data="back")])
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        mes_old = await bot.edit_message_text(chat_id=message.chat.id, message_id=mes.message_id,
                                              text=f'🔍Найдено фильмов или сериалов по запросу: <b>{film}</b>\n<i>🍿Приятного просмотра</i>',
                                              reply_markup=keyboard)
        await state.update_data(mes_id=mes_old)

    else:
        mes_old = await bot.edit_message_text(chat_id=message.chat.id, message_id=mes.message_id,
                                              text=f'Фильм или сериал: <b>{film}</b> не найден!',
                                              reply_markup=keyboard_d)
        await state.update_data(mes_id=mes_old)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await state.set_state()


@dp.callback_query(F.data == 'recommends')
async def recc(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = data.get('mes_id')
    user_id = callback.from_user.id
    a = await check_sub_channel(state, callback.message, user_id=user_id)
    if a:
        mes = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                          text='<b>🔍Поиск фильмов/сериалов...</b>')
        await state.update_data(mes_id=mes)
        kb = []
        titles, links = await get_Rec()
        for title, link in zip(titles, links):
            kb.append([types.InlineKeyboardButton(text=f'🎥{title}', url=link)])
        kb.append([types.InlineKeyboardButton(text='🔄️', callback_data="refresh")])
        kb.append([types.InlineKeyboardButton(text='◀️', callback_data="back")])
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                          text='🔍Нашел несколько фильмов/сериалов, которые могут тебе понравиться\n<i>🍿Приятного просмотра</i>',
                                          reply_markup=keyboard)
        await state.update_data(mes_id=mes)


@dp.callback_query(F.data == 'refresh')
async def ref_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    a = await check_sub_channel(state, callback.message, user_id=user_id)
    if a:
        data = await state.get_data()
        mes = data.get('mes_id')
        mes = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                          text='<b>🔍Поиск фильмов/сериалов...</b>')
        await state.update_data(mes_id=mes)
        kb = []
        titles, links = await get_Rec()
        for title, link in zip(titles, links):
            kb.append([types.InlineKeyboardButton(text=f'🎥{title}', url=link)])
        kb.append([types.InlineKeyboardButton(text='🔄️', callback_data="refresh")])
        kb.append([types.InlineKeyboardButton(text='◀️', callback_data="back")])
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                          text='🔍Нашел несколько фильмов/сериалов, которые могут тебе понравиться\n<i>🍿Приятного просмотра</i>',
                                          reply_markup=keyboard)
        await state.update_data(mes_id=mes)


@dp.callback_query(F.data == 'back')
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = data.get('mes_id')
    user_id = callback.from_user.id
    a = await check_sub_channel(state, callback.message, user_id=user_id)
    if a:
        kb = [
            [types.InlineKeyboardButton(text='🎥Фильм/🍿Сериал', callback_data='film')],
            [types.InlineKeyboardButton(text='🌟Не знаешь, что посмотреть? Кликай!', callback_data='recommends')]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        mes_old = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=mes.message_id,
                                              text='👋Привет, что будем смотреть?', reply_markup=keyboard)
        await state.set_state()
        await state.update_data(mes_id=mes_old)


async def run():
    while True:
        try:
            await bot.delete_webhook(True)
            await base()
            await dp.start_polling(bot, skip_updates=True)
        except TelegramNetworkError as e:
            print(f"Ошибка соединения: {e}")
            await asyncio.sleep(5)
        except TelegramRetryAfter as a:
            print(f"Лимит запросов. Перезапуск {a.retry_after} секунд")
            await asyncio.sleep(a.retry_after)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
