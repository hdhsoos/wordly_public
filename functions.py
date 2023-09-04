from random import randint
import json
import time


def txt_op(name, flag=True):
    f = open(name, 'r', encoding='utf-8')
    sp = []
    if flag:
        for el in f:
            a = el.split()[0]
            if 4 <= len(a) <= 16:
                sp.append(a.lower())
    else:
        for el in f:
            if el[-1] == '\n':
                sp.append(el[:-1])
            else:
                sp.append(el)
    f.close()
    return sp


def txt_sv(LIST, name):
    f = open(name, 'w', encoding='utf-8')
    for el in LIST:
        f.write(str(el))
        if str(el)[-1] != '\n':
            f.write('\n')
    f.close()


def new_word(words, min_len=4, max_len=8):
    x = 10 ** 15
    word = ''
    while x > max_len or x < min_len:
        n = randint(0, len(words) - 1)
        word = words[n]
        x = len(word)
        for el in '.-,"':
            if el in word:
                x = 10 ** 15
    return word


def print_mini_top(STATS, id):
    sorted_tuple = sorted(STATS.items(), key=lambda x: x[1])
    STATS2 = dict(sorted_tuple)
    i = 1
    ans = ''
    user_id = False
    i_main = 0
    for el in STATS2:
        if i > 10:
            break
        ans += '{}. {} - Попыток затрачено: {}.\n'.format(i, el, STATS2[el])
        if el == id:
            user_id = True
            i_main = i
        i += 1
    if id in STATS2:
        if not user_id:
            i = 0
            for el in STATS2:
                i += 1
                if el == id:
                    break
            ans += '\n{}, твоё место в рейтинге: {}. Попыток затрачено {}.'.format(id, i, STATS2[el])
        else:
            ans += '\n{}, твоё место в рейтинге: {}.'.format(id, i_main)
    else:
        ans += '\nТебя нет в рейтинге. Угадай сегодняшнее слово, чтобы попасть в рейтинг. /daily'
    return ans


def print_long_top(STATS, id, max=10):
    sorted_tuple = sorted(STATS.items(), key=lambda x: x[1][7][1])
    sorted_tuple = sorted(sorted_tuple, key=lambda x: x[1][7][0], reverse=True)
    STATS2 = dict(sorted_tuple)
    ans = 'Статистика ведется с 13 июня 2023. Слова дня в рейтинге не учитываются.\n\n'
    i = 1
    user_id = False
    i_main = 0
    for el in STATS2:
        if i > max:
            break
        if STATS2[el][4] != '':
            if STATS2[el][7][0] != 0:
                ans += '{}. {} - Максимальная длина слова: {} - Минимальное число попыток: {}.\n'.format(i,
                                                                                                         STATS2[el][4],
                                                                                                         STATS2[el][7][
                                                                                                             0],
                                                                                                         STATS2[el][7][
                                                                                                             1])
                if el == id:
                    user_id = True
                    i_main = i
                i += 1
    if STATS2[id][7][0] == 0:
        ans += '\n{}, ты пока что не угадывал слова, поэтому тебя нет в рейтинге.'.format(STATS2[id][4])
    elif not user_id:
        i = 0
        for el in STATS2:
            if STATS2[el][4] != '':
                i += 1
                if el == id:
                    break
        ans += '\n{}, твоё место в рейтинге: {}. Максимальная длина слова: {} - Минимальное число попыток: {}.'.format(
            STATS2[id][4], i,
            STATS2[id][7][0], STATS2[id][7][1])
    else:
        ans += '\n{}, твоё место в рейтинге: {}.'.format(STATS2[id][4], i_main)
    return ans


def print_top(STATS, id, weekly=False, max=10):
    sorted_tuple = sorted(STATS.items(), key=lambda x: x[1][1])
    sorted_tuple = sorted(sorted_tuple, key=lambda x: x[1][0], reverse=True)
    STATS2 = dict(sorted_tuple)
    ans = ''
    if weekly:
        ans += 'Еженедельный рейтинг обновляется в 00:00 по UTC +3 каждый четверг.\n\n'
        a = 3  # в еженедельной статистике имя на 3 месте, а в общей на 4
    else:
        a = 4
    i = 1
    user_id = False
    i_main = 0
    for el in STATS2:
        if i > max:
            break
        if STATS2[el][a] != '':
            if weekly and STATS2[el][0] == 0:
                continue
            if STATS2[el][0] != 0:
                x = STATS2[el][1] / STATS2[el][0]
            else:
                x = 0
            x = round(x, 2)
            ans += '{}. {} - слов отгадано: {} - попыток в среднем: {}.\n'.format(i, STATS2[el][a], STATS2[el][0], x)
            if el == id:
                user_id = True
                i_main = i
            i += 1
    if i == 1 and weekly:
        ans += 'На этой неделе ещё никто не играл, ты можешь быть первым!'
        return ans
    if weekly and STATS2[id][0] == 0:
        ans += '\n{}, ты не угадывал слова на этой неделе, поэтому тебя нет в рейтинге.'.format(STATS2[id][a])
    elif not user_id:
        i = 0
        for el in STATS2:
            if STATS2[el][a] != '':
                i += 1
                if el == id:
                    break
        if STATS2[id][0] != 0:
            x = STATS2[id][1] / STATS2[id][0]
        else:
            x = 0
        ans += '\n{}, твоё место в рейтинге: {}. Cлов отгадано: {} - попыток в среднем: {}'.format(STATS2[id][a], i,
                                                                                                   STATS2[id][0], x)
    else:
        ans += '\n{}, твоё место в рейтинге: {}.'.format(STATS2[id][a], i_main)
    return ans


def proverka(inp, word, aid, ALP):
    x = len(word)
    res = [' '] * x
    prov = {}
    for i in range(x):
        if inp[i] == word[i]:
            res[i] = '🟩'  # зеленый
            ALP[aid][3][i] = inp[i]
            if inp[i] not in prov:
                prov[inp[i]] = 1
            else:
                prov[inp[i]] += 1
            if inp[i] in ALP[aid][1]:
                del ALP[aid][1][ALP[aid][1].index(inp[i])]
            if inp[i] not in ALP[aid][0]:
                ALP[aid][0] = ALP[aid][0] + [inp[i]]
        elif inp[i] not in word:
            res[i] = '🟥'  # красный
            if inp[i] in ALP[aid][1]:
                del ALP[aid][1][ALP[aid][1].index(inp[i])]
    for i in range(x):
        if inp[i] != word[i] and inp[i] in word:
            if inp[i] in prov:
                if prov[inp[i]] < word.count(inp[i]):
                    res[i] = '🟨'  # желтый
                    prov[inp[i]] += 1
                    if inp[i] not in ALP[aid][0]:
                        ALP[aid][0] = ALP[aid][0] + [inp[i]]
                    if inp[i] in ALP[aid][1]:
                        del ALP[aid][1][ALP[aid][1].index(inp[i])]
                else:
                    res[i] = '🟥'  # красный
            else:
                res[i] = '🟨'  # желтый
                prov[inp[i]] = 1
                if inp[i] not in ALP[aid][0]:
                    ALP[aid][0] = ALP[aid][0] + [inp[i]]
                if inp[i] in ALP[aid][1]:
                    del ALP[aid][1][ALP[aid][1].index(inp[i])]
    with open('alphabet.json', 'w') as fp:
        json.dump(ALP, fp)
    return ALP, ''.join(res)


def save_log(text):
    file = open('log.txt', 'a')
    print(text)
    file.write(text + time.ctime(
        time.time()) + '\n')
    file.close()


def clear_log():
    file = open('old_log.txt', 'a')
    file2 = open('log.txt', 'r')
    for el in file2:
        file.write(el)
    file.close()
    file2.close()
    file = open('log.txt', 'w')
    file.close()


HITR = {'а': ['a', '@'],
        'б': ['6', 'b'],
        'в': ['v', 'w'],
        'г': ['r', 'g'],
        'д': ['d'],
        'е': ['e'],
        'ё': ['yo'],
        'ж': ['zh', '*'],
        'з': ['3', 'z'],
        'и': ['u'],
        'й': ['i'],
        'к': ['k', 'i{', '|{'],
        'л': ['l', 'ji'],
        'м': ['m'],
        'н': ['n'],
        'о': ['o', '0'],
        'п': ['n', 'p'],
        'р': ['r'],
        'с': ['s'],
        'т': ['t'],
        'у': ['y', 'u'],
        'ф': ['f'],
        'х': ['x', 'h', '}{'],
        'ц': ['c', 'u,', 'ce', 'се'],
        'ч': ['ch'],
        'ш': ['sh'],
        'щ': ['sch'],
        'ы': ['bi'],
        'ю': ['io'],
        'я': ['ya']
        }


def eng_letters(word):
    word = word.lower().replace(" ", "")
    for key, value in HITR.items():
        for el in value:
            if el in word and len(el) > 1:
                word = word.replace(el, key)
    for key, value in HITR.items():
        for el in value:
            if el in word:
                word = word.replace(el, key)
        for letter in value:
            for w in word:
                if letter == w:
                    word = word.replace(w, key)
    return word
