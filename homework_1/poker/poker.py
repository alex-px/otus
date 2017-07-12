#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета. Черный джокер '?B' может быть
# использован в качестве треф или пик любого ранга, красный
# джокер '?R' - в качестве черв и бубен люього ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------

from collections import Counter
from itertools import combinations


RANKS_ORDER = "123456789TJQKA"


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    elif kind(4, ranks):
        return 7, kind(4, ranks), kind(1, ranks)
    elif kind(3, ranks) and kind(2, ranks):
        return 6, kind(3, ranks), kind(2, ranks)
    elif flush(hand):
        return 5, ranks
    elif straight(ranks):
        return 4, max(ranks)
    elif kind(3, ranks):
        return 3, kind(3, ranks), ranks
    elif two_pair(ranks):
        return 2, two_pair(ranks), ranks
    elif kind(2, ranks):
        return 1, kind(2, ranks), ranks
    else:
        return 0, ranks


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент), отсортированный от большего к меньшему"""
    return sorted(RANKS_ORDER.index(card[0]) for card in hand)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits_in_hand = Counter((card[1] for card in hand))
    return len(suits_in_hand) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return ranks[0] * 5 + 10 == sum(ranks)  # sum of arithmetic progression


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    filtered_ranks = [k for k, v in Counter(ranks).items() if v == n]
    if filtered_ranks:
        return max(filtered_ranks)
    return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    filtered_ranks = [k for k, v in Counter(ranks).items() if v == 2]
    if len(filtered_ranks) == 2:
        return sorted(filtered_ranks)
    return None


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    calculated_ranks = ((hand_rank(comb), comb)
                        for comb in combinations(hand, 5))
    return list(max(calculated_ranks)[1])


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def test_flush():
    print("test_flush...")
    assert flush("6C 7C 8C 9C TC".split())
    assert not flush("6C 7C 8D 9C TC".split())
    print("test_flush.........passed")


def test_card_ranks():
    print("test_card_ranks...")
    assert (card_ranks("QC 7C JC 9C TC".split())
           == list(map(RANKS_ORDER.index, "79TJQ")))
    print("test_card_ranks.........passed")


def test_straight():
    print("test_straight...")
    assert straight(card_ranks("89TJQ"))
    # TODO Ace in the straight A2345
    # assert straight(list(map(RANKS_ORDER.index, ["A", "2", "3", "4", "5"])))
    assert not straight(card_ranks("89TJK"))
    print("test_straight..........passed")


def test_kind():
    print("test_kind.....")
    assert kind(3, card_ranks("88T8Q")) == RANKS_ORDER.index("8")
    assert kind(3, card_ranks("88T88")) is None
    assert kind(3, card_ranks("87T8Q")) is None
    assert kind(2, card_ranks("87T87")) == RANKS_ORDER.index("8")
    assert kind(1, card_ranks("88T88")) == RANKS_ORDER.index("T")
    print("test_kind..........passed")


def test_two_pair():
    print("test_two_pair.....")
    assert two_pair(card_ranks("88TQQ")) == card_ranks("8Q")
    assert two_pair(card_ranks("88T8T")) is None
    assert two_pair(card_ranks("87T8Q")) is None
    print("test_two_pair..........passed")


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    assert (sorted(best_hand("8D 9C 2H 3C 5D 4S AH".split()))
            == ['AH', '2H', '3C', '4S', '5D'])
    print('OK')
    return 'test_best_hand passes'


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_flush()
    test_card_ranks()
    test_straight()
    test_kind()
    test_two_pair()
    test_best_hand()
    # test_best_wild_hand()
