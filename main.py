import time
from aiogram import Bot, Dispatcher, executor, types
from functions import txt_op, new_word, print_top, proverka
import json

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
    STATS = json.load(fh)  # список всех юзеров, их статистики (слова, попытки, текущее слово, ник)
with open('AN.json', 'r') as fh:
    AN = json.load(fh)  # статистика того, какой длины люди выбирают слова
with open('alphabet.json', 'r') as fh:
    ALP = json.load(fh)  # специально для /hint, сколько букв каждый пользователь уже проверил
with open('flags.json', 'r') as fh:
    FLAG = json.load(fh)  # переместила флаги в отдельный файл и словарь, чтобы было удобнее


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    global STATS, ALP, FLAG
    if str(message.from_user.id) not in STATS:  # если пользователь заходит впервые
        # если не заифать, можно случайно сбросить все данные пользователя
        STATS[str(message.from_user.id)] = [0, 0, 0, "", "", 0]
        # сколько слов отгадано, суммарное время попыток, сколько попыток, слово, никнейм, подсказок
        with open('result.json', 'w') as fp:
            json.dump(STATS, fp)  # сохранили :)
    if str(message.from_user.id) not in ALP:
        ALP[str(message.from_user.id)] = []
        with open('alphabet.json', 'w') as fp:
            json.dump(ALP, fp)
    if str(message.from_user.id) not in FLAG:
        FLAG[str(message.from_user.id)] = ["False", "False", "False"]
        # задан ли вопрос про длину, задан ли вопрос про ник, задан ли вопрос про ошибки
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
    file = open('log.txt', 'a')
    file.write(str(message.from_user.id) + ' ' + time.ctime(time.time()) + '\n')  # сохранили время отправки /start
    file.close()
    await message.answer(
        "Привет!\nЯ бот для игры в Wordle на русском языке. Расскажу правила игры. Я загадываю слово и говорю тебе только его длину. Твоя задача - писать слова, а я буду говорить, какие буквы совпали, а какие нет.\nЗеленый смайлик означает, что буква находится на том же месте, что и в загаданном слове, желтый, что буква есть, но находится в другом месте, красный, что буквы в слове нет. Если в слове две одинаковые буквы, но одна отмечена, а другая нет, - значит в загаданном слове только одна такая буква. Я ещё учусь и иногда могу загадать неудачное слово, но ты всегда можешь пожаловаться на него с помощью команды /bug. Желаю тебе удачи!\nДля просмотра доступных команд и функций нажми /help. Также используйте /top, чтобы попасть в список лучших игроков!\nНажми /new_word или отправь число, чтобы начать :)")


@dp.message_handler(commands=['stats'])
async def stat(message: types.Message):
    if str(message.from_user.id) in STATS:
        if STATS[str(message.from_user.id)][0] != 0:
            popi = STATS[str(message.from_user.id)][1] / STATS[str(message.from_user.id)][0]
            popi = round(popi, 5)  # количество попыток
            p = STATS[str(message.from_user.id)][5] / STATS[str(message.from_user.id)][0]
            p = round(p, 5)  # количество подсказок
            await message.answer(
                'Статистика:\nСлов отгадано: {}\nСреднее количество попыток: {}\nСреднее количество подсказок: {}'.format(
                    str(STATS[str(message.from_user.id)][0]), str(popi), str(p)))
        else:
            sl = STATS[str(message.from_user.id)][0]
            await message.answer(
                'Статистика:\nСлов отгадано: {}\nСреднее количество попыток: {}\nСреднее количество подсказок: {}'.format(
                    str(sl), '0.0', '0.0'))
    else:
        await message.answer('Статистика не найдена. Может помочь отправить команду /start.')


@dp.message_handler(commands=['new_word'])
async def new(message: types.Message):
    global FLAG
    if str(message.from_user.id) not in STATS:
        await message.answer('Произошла ошибка. Попробуйте отправить /start')
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


@dp.message_handler(commands=['rassilka'])
async def ras(message: types.Message):
    global STATS
    RASS = ['2078134833', '1974111871', '1663532573']
    # секретная функция чтобы отправлять рассылки
    if str(message.from_user.id) == '397472187':
        # for el in RASS:
        #    await bot.send_message(el, "Пожалуйста, для корректной работы бота отправьте /start")
        await message.answer('Готово')
    else:
        await message.answer('Ошибка')


@dp.message_handler(commands=['stop'])
async def stopit(message: types.Message):
    global FLAG, STATS, ALP
    if str(message.from_user.id) not in STATS:
        await message.answer('Произошла ошибка. Попробуйте отправить /start')
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
                'Хорошо, не будем смотреть рейтинг. Нажми /start, чтобы узнать правила, или /new_word, чтобы начать новую игру.')
        elif FLAG[str(message.from_user.id)][2] == "True":
            # если у нас задан вопрос про ошибки
            FLAG[str(message.from_user.id)][2] = "False"
            await message.answer("""Хорошо, не будем писать жалобу. Если найдешь проблему, обязательно пиши!""")
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
        else:
            if STATS[str(message.from_user.id)][3] != "":
                # если у нас есть какое-то слово загаданное
                await message.answer(
                    "Слово было: {}. Повезет в другой раз :) \nПожаловаться на слово - /bug. \nНажми /new_word, чтобы начать новую игру.".format(
                        STATS[str(message.from_user.id)][3]))
                STATS[str(message.from_user.id)][3] = ''  # больше нет слова :)
                STATS[str(message.from_user.id)][2] = 0  # и попыток снова ноль
                ALP[str(message.from_user.id)] = []  # и алфавитика больше нет
                with open('result.json', 'w') as fp:
                    json.dump(STATS, fp)
                with open('alphabet.json', 'w') as fp:
                    json.dump(ALP, fp)
                print('слово не отгадано')
                print(STATS)
            else:
                await message.answer(
                    'Игра и так не идёт, нечего останавливать. Нажми /start, чтобы узнать, что делает этот бот и /new_word, чтобы начать игру.')


@dp.message_handler(commands=['help'])
async def ahelp(message: types.Message):
    await message.answer('''/start - правила игры
/new_word - новая игра
/hint - подсказка
/stop - сдаться
/stats - статистика
/top - рейтинг лучших игроков
/help - список команд - сообщить об ошибке или неудачном слове''')


@dp.message_handler(commands=['bug'])
async def bug(message: types.Message):
    global FLAG
    if str(message.from_user.id) not in STATS:
        await message.answer('Произошла ошибка. Попробуйте отправить /start')
    else:
        FLAG[str(message.from_user.id)][2] = "True"  # задан вопрос про ошибки
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            '''Напиши, пожалуйста, об ошибке или слове, которое на твой взгляд не подходит для игры. Если передумал, нажми /stop.''')


@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    global STATS, FLAG
    if str(message.from_user.id) not in STATS:
        await message.answer('Произошла ошибка. Попробуйте отправить /start')
    elif STATS[str(message.from_user.id)][4] == '':
        # если у пользователя нет ника
        FLAG[str(message.from_user.id)][1] = "True"  # задан вопрос про ник
        with open('flags.json', 'w') as fp:
            json.dump(FLAG, fp)
        await message.answer(
            'Чтобы посмотреть рейтинг, нужно ввести свое имя. Вводя имя, ты даешь согласие, что другие пользователи будут видеть твое имя и количество отгаданных слов. Если не хочешь, нажми /stop.')
    else:
        await message.answer(print_top(STATS))


@dp.message_handler(commands=['hint'])
async def hint(message: types.Message):
    global ALP
    if str(message.from_user.id) not in STATS:
        await message.answer('Произошла ошибка. Попробуйте отправить /start')
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
            await message.answer("Произошла ошибка. Может помочь отправить команду /start.")
    else:
        await message.answer("Игра не идёт, нечего подсказать.")


@dp.message_handler()
async def echo(message: types.Message):
    global STATS, ALP, FLAG
    try:
        if FLAG[str(message.from_user.id)][1] == "True":
            # если задан вопрос про ник
            FLAG[str(message.from_user.id)][1] = "False"
            STATS[str(message.from_user.id)][4] = message.text
            with open('result.json', 'w') as fp:
                json.dump(STATS, fp)
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
            await message.answer(print_top(STATS))
        elif FLAG[str(message.from_user.id)][2] == "True":
            # если задан вопрос про баг
            FLAG[str(message.from_user.id)][2] = "False"
            with open('flags.json', 'w') as fp:
                json.dump(FLAG, fp)
            ans = str(message.from_user.id) + ': ' + message.text
            with open('bugs.txt', 'a') as fp:
                fp.write(ans)
                fp.write('\n')
            ans = '❗️Была оставлена жалоба пользователем ' + ans
            await message.answer("Спасибо! Жалоба записана. Постараемся исправить в ближайшее время.")
            await bot.send_message('397472187', ans)
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
                                                      ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л',
                                                       'м',
                                                       'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ',
                                                       'ъ',
                                                       'ы', 'ь', 'э', 'ю', 'я'],
                                                      0,
                                                      ['_'] * len(word)]
                    STATS[str(message.from_user.id)][3] = word
                    FLAG[str(message.from_user.id)][0] = "False"
                    print(STATS)
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
                await message.answer('Нажми /start, чтобы узнать, что делает этот бот, и /new_word, чтобы начать игру.')
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
                    STATS[str(message.from_user.id)][3] = ''  # все, больше слова нет
                    STATS[str(message.from_user.id)][0] += 1  # угаданных слов стало больше
                    x = STATS[str(message.from_user.id)][2] + 1
                    STATS[str(message.from_user.id)][1] += x  # и попыток тоже
                    STATS[str(message.from_user.id)][2] = 0  # так как слово угадано, счетчик попыток не нужен
                    y = ALP[str(message.from_user.id)][2]
                    STATS[str(message.from_user.id)][5] += y  # это счетчик подсказок)
                    ALP[str(message.from_user.id)] = []  # обнуляем список с буквами
                    with open('result.json', 'w') as fp:
                        json.dump(STATS, fp)
                    with open('alphabet.json', 'w') as fp:
                        json.dump(ALP, fp)
                    await message.answer(
                        'Поздравляю, ты отгадал слово! \nПопыток было: {} \nПодсказок использовано: {}\nЕсли хочешь поиграть ещё, нажми /new_word'.format(
                            str(x), y))
                    print('слово отгадано')
                    print(STATS)
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
        await message.answer('Произошла ошибка. Попробуйте отправить /start')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
