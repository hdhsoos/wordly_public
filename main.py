from aiogram import Bot, Dispatcher, executor, types
from functions import *
import json
import asyncio
import aioschedule
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = ''

bot = Bot(token=API_TOKEN)  # классические пункты для работы с aiogram
dp = Dispatcher(bot)
WORDS = []  # список слов для проверки существования слов для отгадывания
mini_words = []  # список слов для загадывания
WORDS += txt_op('russian.txt')
WORDS += txt_op('deleted_words.txt')
mini_words += txt_op('russian_nouns.txt')
WORDS += mini_words
with open('result.json', 'r') as fh:
    STATS = json.load(fh)  # список всех юзеров, их статистики
    # сколько слов отгадано, суммарное время попыток, сколько попыток, слово, никнейм, подсказок, слов дня, самое длинное угаданное слово и его попытки
with open('weekly.json', 'r') as fh:
    WEEK_STATS = json.load(fh)  # статистика пользователей за неделю (слова, попытки, подсказки, ник)
with open('AN.json', 'r') as fh:
    AN = json.load(fh)  # статистика того, какой длины люди выбирают слова
with open('alphabet.json', 'r') as fh:
    ALP = json.load(fh)  # специально для /hint, сколько букв каждый пользователь уже проверил
with open('flags.json', 'r') as fh:
    FLAG = json.load(fh)  # переместила флаги в отдельный файл и словарь, чтобы было удобнее
with open('word_day.json', 'r') as fh:
    WORD_DAY = json.load(fh)  # отдельный словарь для слова дня, чтобы не переделывать огромные архивы
# ["ключ": [согласен ли на рассылку, отгадано ли слово]]
with open('daily_top.json', 'r') as fh:  # отдельный словарь для ежедневного топа
    DAILY_TOP = json.load(fh)
day_word, idea, last_day_word, last_idea = txt_op('last_actual.txt', False)
# достаем слово дня и вчерашнее слово из специального файла
WORDS.append(day_word)  # на всякий :) мало ли
BANNED = txt_op('banned.txt', False)
RAS_FLAG = False  # вопрос на ввод текста рассылки
BAN_FLAG = False  # вопрос для ввода нового бана
UNBAN_FLAG = False  # вопрос для ввода нового разбана
CH_RE = False  # вопрос для снятия флага у одного пользователя
BAN = txt_op('ban.txt')

urlkb = InlineKeyboardMarkup(row_width=1)  # создание кнопок
urlButton = InlineKeyboardButton(text='Рейтинг за все время', callback_data="full")
urlButton2 = InlineKeyboardButton(text='Рейтинг за неделю', callback_data="week")
urlButton3 = InlineKeyboardButton(text='Рейтинг слова дня', callback_data="day")
urlButton4 = InlineKeyboardButton(text='Самое длинное слово', callback_data="long")
urlkb.add(urlButton, urlButton2, urlButton3, urlButton4)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    global STATS, ALP, FLAG, WORD_DAY, WEEK_STATS
    if str(message.from_user.id) not in STATS:  # если пользователь заходит впервые
        # если не заифать, можно случайно сбросить все данные пользователя
        save_log('Новый пользователь: {} '.format(str(message.from_user.id)))
        STATS[str(message.from_user.id)] = [0, 0, 0, "", "", 0, 0, [0, 0]]
        # сколько слов отгадано, суммарное время попыток, сколько попыток, слово, никнейм, подсказок, слов дня, самое длинное угаданное слово и его попытки
        with open('result.json', 'w') as fp:
            json.dump(STATS, fp)  # сохранили :)
    if str(message.from_user.id) not in WEEK_STATS:
        WEEK_STATS[str(message.from_user.id)] = [0, 0, 0, ""]
        # слова, попытки, подсказки, ник
        with open('weekly.json', 'w') as fp:
            json.dump(WEEK_STATS, fp)
    if str(message.from_user.id) not in ALP:
        ALP[str(message.from_user.id)] = []
        with open('alphabet.json', 'w') as fp:
            json.dump(ALP, fp)
    if str(message.from_user.id) not in FLAG:
        FLAG[str(message.from_user.id)] = ["False", "False", "False", "False"]
        # задан ли вопрос про длину, задан ли вопрос про ник, задан ли вопрос про ошибки, угадывается ли слово дня
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
    if str(message.from_user.id) not in WORD_DAY:
        WORD_DAY[str(message.from_user.id)] = ["False", "False"]
        # согласен ли на рассылку, угадано ли слово дня
        with open('word_day.json', 'w') as fp:
            json.dump(WORD_DAY, fp)
    if STATS[str(message.from_user.id)][4] == '':
        save_log('Пользователь {} отправил /start '.format(str(message.from_user.id)))
    else:
        save_log('Пользователь {} отправил /start '.format(STATS[str(message.from_user.id)][4]))
    await message.answer(
        "Привет!\nЯ бот для игры в Wordle на русском языке. Расскажу правила игры. Я загадываю слово и говорю тебе только его длину. Твоя задача - писать слова, а я буду говорить, какие буквы совпали, а какие нет.\nЗеленый смайлик означает, что буква находится на том же месте, что и в загаданном слове, желтый, что буква есть, но находится в другом месте, красный, что буквы в слове нет. Если в слове две одинаковые буквы, но одна отмечена, а другая нет, - значит в загаданном слове только одна такая буква. Мой словарь тщательно фильтруется, но я все ещё могу загадать неудачное слово, если так будет, ты можешь пожаловаться с помощью команды /bug. Желаю тебе удачи!\nДля просмотра доступных команд и функций нажми /help, в /faq есть ответы на вопросы. Также используй /top, чтобы попасть в список лучших игроков! Можешь попытаться угадать слово дня /daily.\nНажми /new_word или отправь число, чтобы начать :)")


@dp.message_handler(commands=['stats'])
async def stat(message: types.Message):
    if str(message.from_user.id) in STATS:
        if STATS[str(message.from_user.id)][0] != 0:
            popi = STATS[str(message.from_user.id)][1] / STATS[str(message.from_user.id)][0]
            popi = round(popi, 2)  # количество попыток
            p = STATS[str(message.from_user.id)][5] / STATS[str(message.from_user.id)][0]
            p = round(p, 2)  # количество подсказок
            if str(message.from_user.id) == '397472187':
                w = 0
                for el in WEEK_STATS:
                    if WEEK_STATS[el][0] != 0: w += 1
                ras = 0
                for el in WORD_DAY:
                    if WORD_DAY[el][0] == "True": ras += 1
                await message.answer(
                    'Статистика:\nСлов отгадано: {}\nСлов дня отгадано: {}\nСреднее количество попыток: {}\nСреднее количество подсказок: {}\nМаксимальная длина угаданного слова: {}\n\nВсего пользователей в боте: {}\nПользователей за неделю: {}\nПодписано на рассылку: {}'.format(
                        str(STATS[str(message.from_user.id)][0]), str(STATS[str(message.from_user.id)][6]), str(popi),
                        str(p), str(STATS[str(message.from_user.id)][7][0]), len(STATS), w, ras))
            else:
                await message.answer(
                    'Статистика:\nСлов отгадано: {}\nСлов дня отгадано: {}\nСреднее количество попыток: {}\nСреднее количество подсказок: {}\nМаксимальная длина угаданного слова: {}'.format(
                        str(STATS[str(message.from_user.id)][0]), str(STATS[str(message.from_user.id)][6]), str(popi),
                        str(p), str(STATS[str(message.from_user.id)][7][0])))
        else:
            sl = STATS[str(message.from_user.id)][0]
            await message.answer(
                'Статистика:\nСлов отгадано: {}\nСлов дня отгадано: {}\nСреднее количество попыток: {}\nСреднее количество подсказок: {}'.format(
                    str(sl), str(sl), '0.0', '0.0', str(STATS[str(message.from_user.id)][7][0])))
    else:
        await message.answer('Статистика не найдена. Может помочь отправить команду /start.')


@dp.message_handler(commands=['new_word'])
async def new(message: types.Message):
    global FLAG
    if str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он брал новое слово '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start.')
    else:
        if FLAG[str(message.from_user.id)][1] == "True":
            # задан ли вопрос про никнейм
            await message.answer('Сначала введи своё имя, если не хочешь, нажми /stop.')
        elif STATS[str(message.from_user.id)][3] != "":
            # начата ли игра
            await message.answer('Игра уже идет. Если хочешь сдаться, нажми /stop.')
        else:
            FLAG[str(message.from_user.id)][0] = "True"  # задан вопрос про длину слова
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
            await message.answer(
                'Какой длины загадать слово? Напиши только число от 4 до 16. Если хочешь случайную длину, напиши 0.')


@dp.message_handler(commands=['send_log'])
async def selog(message: types.Message):
    global STATS
    # секретная функция чтобы посмотреть лог
    if str(message.from_user.id) == '397472187':
        res = ''
        try:
            file2 = open('log.txt', 'r')
            x = 0
            for el in file2:
                x += 1
            file2.close()
            file2 = open('log.txt', 'r')
            if x > 10:
                x = x - 10
                i = 0
                for el in file2:
                    i += 1
                    if i > x:
                        res += el
            else:
                for el in file2:
                    res += el
            await bot.send_message('397472187', res)
        except:
            await message.answer('Ошибка')
    else:
        await message.answer('Ошибка')


@dp.message_handler(commands=['rassilka'])
async def ras(message: types.Message):
    global STATS, RAS_FLAG
    # секретная функция чтобы отправлять рассылки
    if str(message.from_user.id) == '397472187':
        if BAN_FLAG is True or UNBAN_FLAG is True or RAS_FLAG is True or CH_RE is True:
            await message.answer('Сначала закончи прошлое действие или нажми /stop')
        else:
            RAS_FLAG = True
            await message.answer('Введи текст сообщения для рассылки. Если передумал, нажми /stop')
    else:
        await message.answer('Ошибка')


@dp.message_handler(commands=['ban'])
async def ban(message: types.Message):
    global BAN_FLAG
    if str(message.from_user.id) == '397472187':
        if BAN_FLAG is True or UNBAN_FLAG is True or RAS_FLAG is True or CH_RE is True:
            await message.answer('Сначала закончи прошлое действие или нажми /stop')
        else:
            BAN_FLAG = True
            await message.answer('Введи id человека, которого хочешь заблокировать. Если передумал, нажми /stop')
    else:
        await message.answer('Ошибка')


@dp.message_handler(commands=['unban'])
async def unban(message: types.Message):
    global UNBAN_FLAG
    if str(message.from_user.id) == '397472187':
        if BAN_FLAG is True or UNBAN_FLAG is True or RAS_FLAG is True or CH_RE is True:
            await message.answer('Сначала закончи прошлое действие или нажми /stop')
        else:
            UNBAN_FLAG = True
            await message.answer('Введи id человека, которого хочешь разблокировать. Если передумал, нажми /stop')
    else:
        await message.answer('Ошибка')


@dp.message_handler(commands=['faq'])
async def faq(message: types.Message):
    await message.answer("""- Как играть?
- Правила игры есть в тексте, который появляется при отправке команды /start.
    
- Можно ли играть в этого бота с друзьями?
- Нет, этот бот не предназначен для совместной игры. Оригинальная игра wordle также не расчитана на игру в группе. Если вы хотите, вы можете сесть рядом и угадывать слова, но функция мультиплеера не предусмотрена. Ты можешь добавить бота в беседу, но он не будет работать с несколькими пользователями. Общение будет такое же, как в личных сообщениях. При этом, если ты до этого не общался с ботом и будешь отправлять команды, бот может сломаться. Пожалуйста, отправь /start при первом контакте с ботом. В личных сообщениях отправка команды /start обязательна и происходит автоматически, а в беседах эта необходимость упускается. В принципе бот вообще не предназначен для общения в беседах, но в телеграм любого бота можно добавить в группу.
    
- У меня произошла ошибка, что делать?
- Ошибки бывают совсем разные. Этого бота написал программист-одиночка, так что вполне естественно, что бот не идеален. Ошибки могут быть из-за того, что бота используют не по назначению, например, в беседе. К тому же ошибки могут возникнуть на стороне телеграма: несколько раз пользователи уже сталкивались с ошибкой, которая произошла из-за глюков серверов телеграма. Также могут быть настоящие ошибки в коде. Если ты столкнулся с какой-то повторяющейся ошибкой, используй команду /bug. Если команда /bug не работает, значит ты либо не отправил /start, либо произошла какая-то глобальная ошибка серверов. В жалобе, пожалуйста, опиши проблему максимально подробно, можешь оставить свой url, чтобы с тобой было возможно связаться.
    
- Что за слово такое? Такое слово нельзя загадывать, как я должен был его угадать? А почему нет этого слова? Оно точно существует >:(
- Словарь фильтровался вручную. Он не идеален, наименее тщательно отфильтрованны длинные слова, так как их угадывают реже. Ты можешь помочь и пожаловаться на слово, которое тебе не понравилось. Просто нажми /bug и напиши, какое слово лучше удалить. Или наоборот, какое-то слово может не быть в словаре. Тогда нужно написать в жалобе, что слова в словаре нет. Все жалобы изучаются и все проблемы будут исправлены!

- Как сменить ник?
- Используй команду /clear, чтобы сбросить ник, а затем отправь /top, /daily или /daily_top и введи новый ник. Пожалуйста, придумай приличный ник, чтобы всем было приятно пользоваться ботом. Программист бота оставляет за собой право удалить твой ник, если он будет содержать неуместные высказывания.

- У меня вопрос!!!!
- Для любого общения с разработчиком просто отправь /bug. Спам и оскорбления будут удаляться, а спамеры блокироваться, учти это.""")


@dp.message_handler(commands=['stop'])
async def stopit(message: types.Message):
    global FLAG, STATS, ALP, WORD_DAY, RAS_FLAG, BAN_FLAG, UNBAN_FLAG
    if str(message.from_user.id) == '397472187' and RAS_FLAG is True:
        RAS_FLAG = False
        await message.answer('Хорошо, не будем отправлять рассылку.')
    elif str(message.from_user.id) == '397472187' and BAN_FLAG is True:
        BAN_FLAG = False
        await message.answer('Хорошо, не будем банить.')
    elif str(message.from_user.id) == '397472187' and UNBAN_FLAG is True:
        UNBAN_FLAG = False
        await message.answer('Хорошо, не будем разбанивать.')
    elif str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он нажал /stop '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start')
    else:
        if FLAG[str(message.from_user.id)][0] == "True":
            # если у нас задан вопрос про количество символов
            FLAG[str(message.from_user.id)][0] = "False"
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
            await message.answer(
                'Хорошо, не будем играть. Нажми /start, чтобы узнать правила, или /new_word, чтобы начать новую игру.')
        elif FLAG[str(message.from_user.id)][1] == "True":
            # если у нас задан вопрос про ник
            FLAG[str(message.from_user.id)][1] = "False"
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
            await message.answer(
                'Хорошо, не будем вводить ник. Нажми /start, чтобы узнать правила, или /new_word, чтобы начать новую игру.')
        elif FLAG[str(message.from_user.id)][2] == "True":
            # если у нас задан вопрос про ошибки
            FLAG[str(message.from_user.id)][2] = "False"
            await message.answer("""Хорошо, не будем писать жалобу. Если найдешь проблему, обязательно пиши!""")
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
        else:
            if STATS[str(message.from_user.id)][3] != "":
                # если у нас есть какое-то слово загаданное
                if FLAG[str(message.from_user.id)][3] == "True":
                    # если загадано слово дня
                    FLAG[str(message.from_user.id)][3] = "False"
                    WORD_DAY[str(message.from_user.id)][1] = "True"
                    if STATS[str(message.from_user.id)][4] == '':
                        save_log('Пользователь {}: слово дня не отгадано '.format(str(message.from_user.id)))
                    else:
                        save_log('Пользователь {}: слово дня не отгадано '.format(STATS[str(message.from_user.id)][4]))
                    await message.answer(
                        'Слово было: {}. {}\n\nОбязательно приходи завтра! Подписывайся на уведомления, чтобы не пропустить следующее слово дня /reminder. Можешь посмотреть рейтинг, нажав /daily_top.\nЕсли хочешь поугадывать случайные слова, нажми /new_word.'.format(
                            str(STATS[str(message.from_user.id)][3]), idea))
                    with open('flags.json', 'w') as fp:
                        json.dump(FLAG, fp)
                    with open('word_day.json', 'w') as fp:
                        json.dump(WORD_DAY, fp)
                else:
                    await message.answer(
                        "Слово было: {}. Повезет в другой раз :) \nЕсли слово кажется неподходящим, можешь на него пожаловаться - /bug. \nНажми /new_word, чтобы начать новую игру.".format(
                            STATS[str(message.from_user.id)][3]))
                    if STATS[str(message.from_user.id)][4] == '':
                        save_log('Пользователь {} не отгадал слово {} '.format(str(message.from_user.id),
                                                                               STATS[str(message.from_user.id)][3]))
                    else:
                        save_log('Пользователь {} не отгадал слово {} '.format(STATS[str(message.from_user.id)][4],
                                                                               STATS[str(message.from_user.id)][3]))
                STATS[str(message.from_user.id)][3] = ''  # больше нет слова :)
                STATS[str(message.from_user.id)][2] = 0  # и попыток снова ноль
                ALP[str(message.from_user.id)] = []  # и алфавитика больше нет
                with open('result.json', 'w') as fp:
                    json.dump(STATS, fp)
                with open('alphabet.json', 'w') as fp:
                    json.dump(ALP, fp)
            else:
                await message.answer(
                    'Игра и так не идёт, нечего останавливать. Нажми /start, чтобы узнать, что делает этот бот и /new_word, чтобы начать игру.')


@dp.message_handler(commands=['help'])
async def ahelp(message: types.Message):
    await message.answer('''/start - правила игры
/new_word - новая игра
/daily - слово дня
/hint - подсказка
/stop - сдаться
/stats - статистика
/top - рейтинг лучших игроков
/daily_top - рейтинг слова дня
/help - список команд 
/faq - ответ на некоторые вопросы
/bug - сообщить об ошибке или неудачном слове
/reminder - отписаться или подписаться на напоминание о слове дня
/clear - удалить ник''')


@dp.message_handler(commands=['reminder'])
async def reminder(message: types.Message):
    global WORD_DAY
    if str(message.from_user.id) not in WORD_DAY:
        save_log('У пользователя {} произошла ошибка, когда он пытался подписаться '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start.')
    elif str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он пытался подписаться '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start.')
    else:
        if WORD_DAY[str(message.from_user.id)][0] == "False":
            WORD_DAY[str(message.from_user.id)][0] = "True"
            if STATS[str(message.from_user.id)][4] == '':
                save_log('Пользователь {} подписался на напоминание '.format(str(message.from_user.id)))
            else:
                save_log('Пользователь {} подписался на напоминание '.format(STATS[str(message.from_user.id)][4]))
            await message.answer(
                '''Теперь тебе будет приходить напоминание о новом слове дня.''')
        else:
            WORD_DAY[str(message.from_user.id)][0] = "False"
            if STATS[str(message.from_user.id)][4] == '':
                save_log('Пользователь {} отписался от напоминания '.format(str(message.from_user.id)))
            else:
                save_log('Пользователь {} отписался от напоминания '.format(STATS[str(message.from_user.id)][4]))
            await message.answer(
                '''Тебе больше не будет приходить напоминание о новом слове дня.''')
        with open('word_day.json', 'w') as fp:
            json.dump(WORD_DAY, fp)


@dp.message_handler(commands=['change_reminder'])
async def ch_re(message: types.Message):
    global CH_RE
    if str(message.from_user.id) == '397472187':
        if BAN_FLAG is True or UNBAN_FLAG is True or RAS_FLAG is True or CH_RE is True:
            await message.answer('Сначала закончи прошлое действие или нажми /stop')
        else:
            CH_RE = True
            await message.answer(
                'Введи id человека, которого хочешь отписать от напоминания. Если передумал, нажми /stop')
    else:
        await message.answer('Ошибка')


async def new_day_word():
    global WORD_DAY, day_word, last_day_word, DAILY_TOP, idea, last_idea, WORDS, FLAG
    last_day_word = day_word
    last_idea = idea
    # генерация слова дня
    for el in WORD_DAY:
        WORD_DAY[el] = [WORD_DAY[el][0], "False"]
    for el in FLAG:
        FLAG[el][3] = "False"
    with open('flags.json', 'w') as fp:
        json.dump(FLAG, fp)
    with open('word_day.json', 'w') as fp:
        json.dump(WORD_DAY, fp)
    DAILY_TOP = {}
    with open('daily_top.json', 'w') as fp:
        json.dump(DAILY_TOP, fp)
    # сначала мы опустили флаг решённости и счетчик попыток для каждого пользователя, а также обнулили ежедневный топ
    NEW_WORD = txt_op('future_words.txt', False)
    day_word = NEW_WORD[0].split()[0]
    WORDS.append(day_word)
    idea = NEW_WORD[1]
    del NEW_WORD[0]
    del NEW_WORD[0]
    txt_sv(NEW_WORD, 'future_words.txt')  # достали из стека актуальное слово и комментарий, а остальное сохранили
    LAST_ACTUAL = [day_word, idea, last_day_word, last_idea]
    txt_sv(LAST_ACTUAL, 'last_actual.txt')
    print('Слово дня загадано.')
    clear_log()
    save_log('---------- ')


async def new_week_top():
    global WEEK_STATS
    for el in STATS:
        WEEK_STATS[el] = [0, 0, 0, STATS[el][4]]  # (слова, попытки, подсказки, ник)
    with open('weekly.json', 'w') as fp:
        json.dump(WEEK_STATS, fp)


async def morning():
    global WORD_DAY
    # напоминалка о слове дня
    for el in WORD_DAY:
        if WORD_DAY[el][0] == "True" and WORD_DAY[el][1] == "False":
            try:
                await bot.send_message(el,
                                       "Привет, слово дня уже ждёт тебя! /daily.\nЕсли не хочешь больше напоминаний, нажми /reminder.")
            except:
                await bot.send_message("397472187", 'Не удалось отправить сообщение пользователю {}'.format(el))


async def scheduler():
    # эта функция проверяет, есть ли 10:00 и если есть, делает напоминание
    aioschedule.every().day.at("6:00").do(morning)
    # эта функция проверяет, есть ли 0:00 и если есть, генерирует слово дня
    aioschedule.every().day.at("21:00").do(new_day_word)
    # эта функция раз в неделю обнуляет топ
    aioschedule.every().wednesday.at("21:00").do(new_week_top)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    # эта функция будет запускаться в самом начале работы программы и будет работать всегда
    asyncio.create_task(scheduler())


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    global STATS, DAILY_TOP
    if str(message.from_user.id) not in STATS:
        save_log(
            'У пользователя {} произошла ошибка, когда он пытался удалить ник '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start.')
    elif STATS[str(message.from_user.id)][4] == "":
        await message.answer("У тебя и так нет ника, нечего удалять.")
    else:
        save_log(
            "Пользователь {} удалил ник {} ".format(str(message.from_user.id), STATS[str(message.from_user.id)][4]))
        STATS[str(message.from_user.id)][4] = ''
        with open('result.json', 'w') as fp:
            json.dump(STATS, fp)
        await message.answer(
            'Старый ник удалён. Захочешь ввести новый - просто отправь /top, /daily или /daily_top. Если ты угадывал слово дня, твой старый ник останется в /daily_top до конца дня, чтобы избежать путаницы.')


@dp.message_handler(commands=['daily'])
async def daily(message: types.Message):
    global WORD_DAY, FLAG, day_word, STATS, ALP
    if str(message.from_user.id) not in STATS:
        save_log(
            'У пользователя {} произошла ошибка, когда он пытался угадать слово дня '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start.')
    elif STATS[str(message.from_user.id)][4] == '':
        FLAG[str(message.from_user.id)][1] = "True"  # задан вопрос про ник
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            'Чтобы угадывать слово дня, нужно ввести свое имя. Другие пользователи будут видеть твой ник и количество отгаданных слов, если ты попадешь в топ 10. Если не хочешь, нажми /stop.')
    elif WORD_DAY[str(message.from_user.id)][1] == "True":
        await message.answer(
            'Ты сегодня уже угадывал слово дня, приходи завтра! Новое слово появится в 00:00 по UTC +3. Подписывайся на уведомления, чтобы не пропустить следующее слово дня /reminder. Ты можешь увидеть рейтинг угадавших с помощью /daily_top. Если хочешь поугадывать случайные слова, нажми /new_word.')
    elif FLAG[str(message.from_user.id)][3] == "True":
        await message.answer(
            'Ты уже угадываешь слово дня прямо сейчас. Если хочешь сдаться, нажми /stop.')
    else:
        FLAG[str(message.from_user.id)][3] = "True"  # Начинаем угадывать слово дня
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        if STATS[str(message.from_user.id)][3] != '':
            await message.answer('Слово, которые ты угадывал, пришлось обнулить. Это было слово {}.'.format(
                STATS[str(message.from_user.id)][3]))
        STATS[str(message.from_user.id)][2] = 0  # попыток ноль
        STATS[str(message.from_user.id)][3] = day_word
        res = '_ ' * len(day_word)
        res += 'букв в слове - {} \nВведи слово или нажми /stop, если надоело. Учти, слово дня можно попытаться угадать только один раз. Подписывайся на уведомления, чтобы не пропустить следующее слово дня /reminder.'.format(
            len(day_word))
        ALP[str(message.from_user.id)] = [[],
                                          ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л',
                                           'м',
                                           'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ',
                                           'ъ',
                                           'ы', 'ь', 'э', 'ю', 'я'],
                                          0,
                                          ['_'] * len(day_word)]
        if STATS[str(message.from_user.id)][4] == '':
            save_log('Пользователь {} отгадывает слово дня '.format(str(message.from_user.id)))
        else:
            save_log('Пользователь {} отгадывает слово дня '.format(STATS[str(message.from_user.id)][4]))
        await message.answer(res)
        with open('result.json', 'w') as fp:
            json.dump(STATS, fp)
        with open('alphabet.json', 'w') as fp:
            json.dump(ALP, fp)


@dp.message_handler(commands=['daily_top'])
async def daily(message: types.Message):
    global DAILY_TOP, FLAG
    if STATS[str(message.from_user.id)][4] == '':
        FLAG[str(message.from_user.id)][1] = "True"  # задан вопрос про ник
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            'Чтобы увидеть рейтинг слова дня, нужно ввести свое имя. Другие пользователи будут видеть твой ник и количество отгаданных слов, если ты попадешь в топ 10. Если не хочешь, нажми /stop.')
    else:
        res = 'Вчерашнее слово дня: {}. {}\n\n'.format(
            last_day_word, last_idea)
        res = res + print_mini_top(DAILY_TOP, STATS[str(message.from_user.id)][4])
        await message.answer(res)


@dp.message_handler(commands=['bug'])
async def bug(message: types.Message):
    global FLAG, BAN
    if str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он жаловался на баг '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start')
    elif str(message.from_user.id) in BAN:
        await message.answer('Для вас функция отправки жалобы отключена.')
        save_log('Заблокированный пользователь не смог отправить жалобу')
    else:
        FLAG[str(message.from_user.id)][2] = "True"  # задан вопрос про ошибки
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            '''Напиши, пожалуйста, об ошибке или слове, которое на твой взгляд не подходит для игры. Если хочешь получить ответ или написать уточнения в сообщения, укажи свой url телеграма. Разработчики не знают, какая у тебя произошла ошибка, так что пиши подробно: что делал, что написал, что бот ответил. Если передумал, нажми /stop.''')


@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    global STATS, FLAG
    if str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он вызвал топ '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start')
    elif STATS[str(message.from_user.id)][4] == '':
        # если у пользователя нет ника
        FLAG[str(message.from_user.id)][1] = "True"  # задан вопрос про ник
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            'Чтобы посмотреть рейтинг, нужно ввести свое имя. Другие пользователи будут видеть твой ник и количество отгаданных слов, если ты попадешь в топ 10. Если не хочешь, нажми /stop.')
    else:
        await message.answer('Выбери, какой из рейтингов хочешь просмотреть:', reply_markup=urlkb)


@dp.callback_query_handler()
async def callbacks_num(callback: types.CallbackQuery):
    await callback.answer()
    if callback.data == "full":
        await callback.message.answer(print_top(STATS, str(callback.from_user.id)))
    elif callback.data == "week":
        await callback.message.answer(print_top(WEEK_STATS, str(callback.from_user.id), True))
    elif callback.data == "day":
        global DAILY_TOP
        res = 'Вчерашнее слово дня: {}. {}\n\n'.format(
            last_day_word, last_idea)
        res = res + print_mini_top(DAILY_TOP, STATS[str(callback.from_user.id)][4])
        await callback.message.answer(res)
    elif callback.data == 'long':
        await callback.message.answer(print_long_top(STATS, str(callback.from_user.id)))


@dp.message_handler(commands=['hint'])
async def hint(message: types.Message):
    global ALP
    if str(message.from_user.id) not in STATS:
        save_log('У пользователя {} произошла ошибка, когда он вызвал подсказку '.format(str(message.from_user.id)))
        await message.answer('Произошла ошибка. Попробуй отправить /start')
    elif STATS[str(message.from_user.id)][3] != "":  # если слово загадано
        if str(message.from_user.id) in ALP:  # если пользователь жал start
            ans = '🟩: '
            ans += ' '.join(ALP[str(message.from_user.id)][3])
            ans += '\n'
            ans += '🟨: '
            ans += ', '.join(ALP[str(message.from_user.id)][0])
            ans += '\n'
            ans += '⬜️: '
            ans += ', '.join(ALP[str(message.from_user.id)][1])
            ALP[str(message.from_user.id)][2] += 1  # сколько раз запрашивали подсказку
            with open('alphabet.json', 'w') as fp:
                json.dump(ALP, fp)
            await message.answer(ans)
        else:
            save_log('У пользователя {} произошла ошибка, когда он вызвал подсказку '.format(str(message.from_user.id)))
            await message.answer("Произошла ошибка. Может помочь отправить команду /start.")
    else:
        await message.answer("Игра не идёт, нечего подсказать.")


@dp.message_handler()
async def echo(message: types.Message):
    global STATS, ALP, FLAG, WORD_DAY, DAILY_TOP, WEEK_STATS, RAS_FLAG, BAN_FLAG, UNBAN_FLAG, BAN, CH_RE
    if str(message.from_user.id) not in STATS:
        await message.answer('Ты новый пользователь? Отправь /start, чтобы пользоваться ботом!')
    else:
        try:
            if FLAG[str(message.from_user.id)][1] == "True":
                # если задан вопрос про ник
                u = True
                word = eng_letters(message.text)
                if word in BANNED or message.text.lower() in BANNED:
                    await message.answer(
                        "Прости, но данный ник недоступен, попробуй другой. Если передумал указывать имя, нажми /stop.")
                    u = False
                else:
                    for el in BANNED:
                        if el.lower() in word or el in message.text.lower():
                            await message.answer(
                                "Прости, но данный ник недоступен, попробуй другой. Если передумал указывать имя, нажми /stop.")
                            u = False
                            break
                    if u:
                        for el in STATS:
                            if STATS[el][4].lower() == message.text.lower():
                                await message.answer(
                                    "Прости, но данный ник занят, попробуй другой. Если передумал указывать имя, нажми /stop.")
                                u = False
                                break
                        if u:
                            FLAG[str(message.from_user.id)][1] = "False"
                            STATS[str(message.from_user.id)][4] = message.text
                            WEEK_STATS[str(message.from_user.id)][3] = message.text
                            save_log(
                                "Пользователь {} создал никнейм {}".format(str(message.from_user.id), message.text))
                            with open('result.json', 'w') as fp:
                                json.dump(STATS, fp)
                            with open('flags.json', 'w') as fp:
                                json.dump(FLAG, fp)
                            with open('weekly.json', 'w') as fp:
                                json.dump(WEEK_STATS, fp)
                            await message.answer(
                                'Приятно познакомиться, {}. Теперь ты можешь просмотреть рейтинг /top или угадать слово дня /daily.'.format(
                                    STATS[str(message.from_user.id)][4]))
            elif FLAG[str(message.from_user.id)][2] == "True":
                # если задан вопрос про баг
                FLAG[str(message.from_user.id)][2] = "False"
                with open('flags.json', 'w') as fp:
                    json.dump(FLAG, fp)
                ans = str(message.from_user.id) + ' ({})'.format(
                    STATS[str(message.from_user.id)][4]) + ': ' + message.text
                with open('bugs.txt', 'a') as fp:
                    fp.write(ans)
                    fp.write('\n')
                ans = '❗️Была оставлена жалоба пользователем ' + ans
                await message.answer("Спасибо! Жалоба записана. Постараемся исправить в ближайшее время.")
                await bot.send_message('397472187', ans)
            elif str(message.from_user.id) == '397472187' and RAS_FLAG is True:
                RAS_FLAG = False
                await message.answer('Начинаем рассылку.')
                for el in STATS:
                    try:
                        await bot.send_message(el, message.text)
                    except:
                        await message.answer('Не удалось отправить сообщение пользователю {}'.format(el))
            elif str(message.from_user.id) == '397472187' and BAN_FLAG is True:
                BAN_FLAG = False
                try:
                    ban_id = int(message.text)
                    if str(ban_id) in STATS:
                        try:
                            BAN.append(str(ban_id))
                            await message.answer('Готово.')
                        except:
                            await message.answer('Не получилось забанить пользователя.')
                    else:
                        await message.answer('Данного пользователя не существует.')
                    txt_sv(BAN, 'ban.txt')
                except:
                    await message.answer('Ошибка ввода.')
            elif str(message.from_user.id) == '397472187' and UNBAN_FLAG is True:
                UNBAN_FLAG = False
                try:
                    ban_id = int(message.text)
                    if str(ban_id) in BAN:
                        try:
                            del BAN[BAN.index(str(ban_id))]
                            await message.answer('Готово.')
                        except:
                            await message.answer('Не получилось разбанить пользователя.')
                    else:
                        await message.answer('Данного пользователя нет в бане.')
                    txt_sv(BAN, 'ban.txt')
                except:
                    await message.answer('Ошибка ввода.')
            elif str(message.from_user.id) == '397472187' and CH_RE is True:
                CH_RE = False
                try:
                    ban_id = int(message.text)
                    if str(ban_id) in WORD_DAY:
                        if WORD_DAY[str(ban_id)][0] == "True":
                            try:
                                WORD_DAY[str(ban_id)] = ["False", WORD_DAY[str(ban_id)][1]]
                                with open('word_day.json', 'w') as fp:
                                    json.dump(WORD_DAY, fp)
                                await message.answer('Готово.')
                            except:
                                await message.answer('Не получилось отписать пользователя.')
                        else:
                            await message.answer('Пользователь не подписан.')
                    else:
                        await message.answer('Данного пользователя не существует.')
                    txt_sv(BAN, 'ban.txt')
                except:
                    await message.answer('Ошибка ввода.')
            elif STATS[str(message.from_user.id)][3] == "" and (FLAG[str(message.from_user.id)][0] == "True" or (
                    message.text in ['4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '0'])):
                # если нет слова и задан вопрос или введено число
                if len(message.text.split()) > 1:
                    await message.answer('Введено неверное число. Если не хочешь играть, нажми /stop.')
                else:
                    answer = message.text
                    if answer in ['4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '0']:
                        AN[answer] += 1
                        with open('AN.json', 'w') as fp:
                            json.dump(AN, fp)
                        if answer == '0':
                            word = new_word(mini_words)
                        else:
                            n = int(answer)
                            word = new_word(mini_words, n, n)
                        res = '_ ' * len(word)
                        res += 'букв в слове - {} \nВведи слово или нажми /stop, если надоело.'.format(len(word))
                        ALP[str(message.from_user.id)] = [[],
                                                          ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к',
                                                           'л',
                                                           'м',
                                                           'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш',
                                                           'щ',
                                                           'ъ',
                                                           'ы', 'ь', 'э', 'ю', 'я'],
                                                          0,
                                                          ['_'] * len(word)]
                        STATS[str(message.from_user.id)][3] = word
                        FLAG[str(message.from_user.id)][0] = "False"
                        if STATS[str(message.from_user.id)][4] == '':
                            save_log('Пользователь {} отгадывает слово {} '.format(str(message.from_user.id), word))
                        else:
                            save_log(
                                'Пользователь {} отгадывает слово {} '.format(STATS[str(message.from_user.id)][4],
                                                                              word))
                        await message.answer(res)
                        with open('result.json', 'w') as fp:
                            json.dump(STATS, fp)
                        with open('alphabet.json', 'w') as fp:
                            json.dump(ALP, fp)
                        with open('flags.json', 'w') as fp:
                            json.dump(FLAG, fp)
                    else:
                        await message.answer('Введено неверное число. Если не хочешь угадывать, нажми /stop.')
            else:
                if STATS[str(message.from_user.id)][3] == "":
                    # если нет слова и написано непонятно что
                    await message.answer(
                        'Нажми /start, чтобы узнать, что делает этот бот, и /new_word, чтобы начать игру.')
                else:
                    answer = message.text.lower()
                    word = STATS[str(message.from_user.id)][3]
                    if len(answer.split()) > 1:
                        await message.answer(
                            'Напиши одно слово, а я скажу, отгадал ты или нет. Если хочешь подсказку, нажми /hint. Если надоело, нажми /stop.')
                    elif len(answer) != len(word):
                        await message.answer(
                            'Слово должно быть такой же длины, как и загаданное. Это длина {}. Если хочешь подсказку, нажми /hint. Если надоело, нажми /stop.'.format(
                                len(word)))
                    elif answer not in WORDS:
                        await message.answer(
                            'Я не знаю такого слова. Если хочешь подсказку, нажми /hint. Если надоело, нажми /stop.')
                    elif answer == word:
                        x = STATS[str(message.from_user.id)][2] + 1  # количество попыток
                        y = ALP[str(message.from_user.id)][2]  # количество подсказок
                        if FLAG[str(message.from_user.id)][3] == "True":
                            FLAG[str(message.from_user.id)][3] = "False"
                            WORD_DAY[str(message.from_user.id)][1] = "True"
                            with open('flags.json', 'w') as fp:
                                json.dump(FLAG, fp)
                            with open('word_day.json', 'w') as fp:
                                json.dump(WORD_DAY, fp)
                            if STATS[str(message.from_user.id)][4] == '':
                                save_log('Пользователь {} отгадал слово дня '.format(str(message.from_user.id)))
                            else:
                                save_log(
                                    'Пользователь {} отгадал слово дня '.format(STATS[str(message.from_user.id)][4]))
                            STATS[str(message.from_user.id)][6] += 1  # угаданных слов дня стало больше
                            DAILY_TOP[STATS[str(message.from_user.id)][4]] = x
                            with open('daily_top.json', 'w') as fp:
                                json.dump(DAILY_TOP, fp)
                            await message.answer(
                                'Поздравляю, ты отгадал слово дня! {}\n\nОбязательно приходи завтра! Подписывайся на уведомления, чтобы не пропустить следующее слово дня /reminder. Можешь посмотреть рейтинг, нажав /daily_top.\nПопыток было: {} \nПодсказок использовано: {}\nЕсли хочешь поугадывать случайные слова, нажми /new_word.'.format(
                                    idea, str(x), str(y)))
                        else:
                            await message.answer(
                                'Поздравляю, ты отгадал слово! \nПопыток было: {} \nПодсказок использовано: {}\nЕсли хочешь поиграть ещё, нажми /new_word.'.format(
                                    str(x), str(y)))
                            if STATS[str(message.from_user.id)][7][0] < len(word) or (
                                    STATS[str(message.from_user.id)][7][0] == len(word) and
                                    STATS[str(message.from_user.id)][7][1] > x):
                                STATS[str(message.from_user.id)][7] = [len(word), x]
                            if STATS[str(message.from_user.id)][4] == '':
                                save_log('Пользователь {} отгадал слово {} '.format(str(message.from_user.id), word))
                            else:
                                save_log(
                                    'Пользователь {} отгадал слово {} '.format(STATS[str(message.from_user.id)][4],
                                                                               word))
                        STATS[str(message.from_user.id)][2] = 0  # так как слово угадано, счетчик попыток не нужен
                        STATS[str(message.from_user.id)][0] += 1
                        WEEK_STATS[str(message.from_user.id)][0] += 1  # угаданных слов стало больше
                        STATS[str(message.from_user.id)][1] += x
                        WEEK_STATS[str(message.from_user.id)][1] += x  # и попыток тоже
                        STATS[str(message.from_user.id)][5] += y
                        WEEK_STATS[str(message.from_user.id)][2] += y  # это счетчик подсказок)
                        STATS[str(message.from_user.id)][3] = ''  # все, больше слова нет
                        ALP[str(message.from_user.id)] = []  # обнуляем список с буквами
                        with open('result.json', 'w') as fp:
                            json.dump(STATS, fp)
                        with open('alphabet.json', 'w') as fp:
                            json.dump(ALP, fp)
                        # (слова, попытки, подсказки, ник)
                        with open('weekly.json', 'w') as fp:
                            json.dump(WEEK_STATS, fp)
                    else:
                        STATS[str(message.from_user.id)][2] += 1  # счетчик попыток ++
                        with open('result.json', 'w') as fp:
                            json.dump(STATS, fp)
                        ALP, ans = proverka(answer, word, str(message.from_user.id), ALP)
                        await message.answer(ans)
                        if STATS[str(message.from_user.id)][2] == 6 and ALP[str(message.from_user.id)][2] == 0:
                            # если пользователь не в курсе или забыл про подсказки и мучается уже долго, предлагаем помощь
                            await message.answer(
                                'Могу помочь: нажми /hint, а я отправлю буквы, которые есть в слове или ещё не были проверены.')
        except:
            save_log('У пользователя {} произошла ошибка '.format(str(message.from_user.id)))
            await message.answer(
                'Произошла ошибка. Может помочь отправить /start. Также можешь сообщить подробности с помощью команды /bug, это очень поможет сделать бота лучше.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
