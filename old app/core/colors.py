from dataclasses import dataclass
from typing import Iterable
from random import Random


@dataclass
class Color(object):
    name: str
    rgb: str
    text_bright: bool
    accessibility_level: int


def get_colors(accessibility: int) -> Iterable[Color]:
    return (i for i in COLORS.values() if i.accessibility_level <= accessibility)


def get_branch_name(accessibility: int, used: Iterable[str]) -> Iterable[str]:
    for i in get_colors(accessibility):
        if i.name not in used:
            yield i.name
    for i in WORDS:
        if i not in used:
            yield i


DEFAULT_COLOR = Color("Czarna", "#000000", True, 1)

COLORS = {
    "Czerwona":     Color("Czerwona", "#cd0032", True, 3),
    "Zielona":      Color("Zielona", "#00700e", True, 3),
    "Niebieska":    Color("Niebieska", "#3254d2", True, 1),
    "Fioletowa":    Color("Fioletowa", "#911eb4", True, 4),
    "Turkusowa":    Color("Turkusowa", "#156f82", False, 3),
    "Magenta":      Color("Magenta", "#b900af", True, 3),
    "Morska":       Color("Morska", "#077267", True, 3),
    "Brązowa":      Color("Brązowa", "#975101", True, 3),
    "Bordowa":      Color("Bordowa", "#800000", True, 2),
    "Oliwkowa":     Color("Oliwkowa", "#696901", True, 4),
    "Morelowa":     Color("Morelowa", "#ffd8b1", False, 4),
    "Granatowa":    Color("Granatowa", "#000075", True, 2),
    "Biała":        Color("Biała", "#ffffff", False, 1),
    "Szara":        Color("Szara", "#a9a9a9", True, 1) 
}

# Rośliny VU, EN oraz CR na bazie https://pl.wikipedia.org/wiki/Polska_czerwona_ksi%C4%99ga_ro%C5%9Blin
WORDS = [
    'Mokrzyca', 'Storczyk', 'Pierwiosnka', 'Ostnica', 'Dzwonek', 'Przygiełka', 'Saussurea', 'Jarząb', 'Miodokwiat', 'Kaldezja', 'Wełnianka', 'Babka', 'Czosnek', 'Turzyca', 'Lobelia', 'Szyplin', 'Gnidosz', 'Perz', 'Stoplamek', 'Ponikło', 'Ciemiężyca', 'Różanecznik', 'Irga', 'Cebulica', 'Łoboda', 'Wieczornik', 'Miłek', 'Storzan', 'Rozrzutka', 'Fiołek', 'Jeżogłówka', 'Karmnik', 'Kręczynka', 'Aldrowanda', 'Przetacznik', 'Stulisz', 'Głodek', 'Czechrzyca', 'Zmienka', 'Jaskier', 'Dziurawiec', 'Poryblin', 'Wierzba', 'Okrzyn', 'Elisma', 'Ostrołódka', 'Potrostek', 'Cyklamen', 'Starodub', 'Wiechlinostrzewa', 'Traganek', 'Dąb', 'Pszonacznik', 'Kiksja', 'Kruszczyk', 'Przesiąkra', 'Brzoza', 'Brzeżyca', 'Rzeżucha', 'Macierzanka', 'Gałuszka', 'Oman', 'Wątlik', 'Wełnianeczka', 'Żmijowiec', 'Rogownica', 'Groszek', 'Mniszek', 'Rozchodnik', 'Widlicz', 'Buławnik', 'Sierpik', 'Tojad', 'Sit', 'Ostrzew', 'Przewiercień', 'Mannica', 'Dyptam', 'Perłówka', 'Przymiotno', 'Lindernia', 'Języczka', 'Kropidło', 'Szachownica', 'Malina', 'Zaraza', 'Chamedafne', 'Mieczyk', 'Selery', 'Kotewka', 'Przytulia', 'Szafirek', 'Szczodrzeniec', 'Tłustosz', 'Skalnica', 'Zanokcica', 'Podejźrzon', 'Wawrzynek', 'Gęsiówka', 'Bylica', 'Wywłócznik', 'Nadbrzeżyca', 'Kukuczka', 'Rdestnica'
]

Random(bytes('Nawiasem mówiąc: przedmioty są bezbarwne',
       encoding='utf-8')).shuffle(WORDS)