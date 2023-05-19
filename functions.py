from random import randint
import json


def txt_op(name):
    f = open(name, 'r', encoding='utf-8')
    sp = []
    for el in f:
        a = el.split()[0]
        if 4 <= len(a) <= 16:
            sp.append(a.lower())
    f.close()
    return sp


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
    print(word)
    return word


def print_top(STATS):
    sorted_tuple = sorted(STATS.items(), key=lambda x: x[1][1])
    sorted_tuple = sorted(sorted_tuple, key=lambda x: x[1][0], reverse=True)
    STATS2 = dict(sorted_tuple)
    i = 1
    ans = ''
    for el in STATS2:
        if i > 10:
            break
        if STATS2[el][4] != '':
            if STATS2[el][0] != 0:
                x = STATS2[el][1] / STATS2[el][0]
            else:
                x = 0
            x = round(x, 5)
            ans += '{}. {} - слов отгадано: {} - попыток в среднем: {}.\n'.format(i, STATS2[el][4], STATS2[el][0], x)
            i += 1
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
