"""
Based on https://sashamaps.net/docs/resources/20-colors/
Animal names from https://list.fandom.com/wiki/List_of_common_animals
"""
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


DEFAULT_COLOR = Color("Grey", "#a9a9a9", True, 1)

COLORS = {
    "Red":      Color("Red", "#e6194B", True, 3),
    "Green":    Color("Green", "#3cb44b", True, 3),
    "Yellow":   Color("Yellow", "#ffe119", False, 1),
    "Blue":     Color("Blue", "#4363d8", True, 1),
    "Orange":   Color("Orange", "#f58231", True, 2),
    "Purple":   Color("Purple", "#911eb4", True, 4),
    "Cyan":     Color("Cyan", "#42d4f4", False, 3),
    "Magenta":  Color("Magenta", "#f032e6", True, 3),
    "Lime":     Color("Lime", "#bfef45", False, 4),
    "Pink":     Color("Pink", "#fabed4", False, 3),
    "Teal":     Color("Teal", "#469990", True, 3),
    "Lavender": Color("Lavender", "#dcbeff", False, 2),
    "Brown":    Color("Brown", "#9A6324", True, 3),
    "Beige":    Color("Beige", "#fffac8", False, 3),
    "Maroon":   Color("Maroon", "#800000", True, 2),
    "Mint":     Color("Mint", "#aaffc3", False, 3),
    "Olive":    Color("Olive", "#808000", True, 4),
    "Apricot":  Color("Apricot", "#ffd8b1", False, 4),
    "Navy":     Color("Navy", "#000075", True, 2),
    "White":    Color("White", "#ffffff", False, 1),
    "Black":    Color("Black", "#000000", True, 1)
}

WORDS = [
    "Aardvark",
    "Alligator",
    "Alpaca",
    "Anaconda",
    "Ant",
    "Antelope",
    "Ape",
    "Aphid",
    "Armadillo",
    "Asp",
    "Ass",
    "Baboon",
    "Badger",
    "Bald Eagle",
    "Barracuda",
    "Bass",
    "Basset Hound",
    "Bat",
    "Bear",
    "Beaver",
    "Bedbug",
    "Bee",
    "Beetle",
    "Bird",
    "Bison",
    "Black panther",
    "Black Widow Spider",
    "Blue Jay",
    "Blue Whale",
    "Bobcat",
    "Buffalo",
    "Butterfly",
    "Buzzard",
    "Camel",
    "Caribou",
    "Carp",
    "Cat",
    "Caterpillar",
    "Catfish",
    "Cheetah",
    "Chicken",
    "Chimpanzee",
    "Chipmunk",
    "Cobra",
    "Cod",
    "Condor",
    "Cougar",
    "Cow",
    "Coyote",
    "Crab",
    "Crane",
    "Cricket",
    "Crocodile",
    "Crow",
    "Cuckoo",
    "Deer",
    "Dinosaur",
    "Dog",
    "Dolphin",
    "Donkey",
    "Dove",
    "Dragonfly",
    "Duck",
    "Eagle",
    "Eel",
    "Elephant",
    "Emu",
    "Falcon",
    "Ferret",
    "Finch",
    "Fish",
    "Flamingo",
    "Flea",
    "Fly",
    "Fox",
    "Frog",
    "Goat",
    "Goose",
    "Gopher",
    "Gorilla",
    "Grasshopper",
    "Hamster",
    "Hare",
    "Hawk",
    "Hippopotamus",
    "Horse",
    "Hummingbird",
    "Humpback Whale",
    "Husky",
    "Iguana",
    "Impala",
    "Kangaroo",
    "Ladybug",
    "Leopard",
    "Lion",
    "Lizard",
    "Llama",
    "Lobster",
    "Mongoose",
    "Monitor lizard",
    "Monkey",
    "Moose",
    "Mosquito",
    "Moth",
    "Mountain goat",
    "Mouse",
    "Mule",
    "Octopus",
    "Orca",
    "Ostrich",
    "Otter",
    "Owl",
    "Ox",
    "Oyster",
    "Panda",
    "Parrot",
    "Peacock",
    "Pelican",
    "Penguin",
    "Perch",
    "Pheasant",
    "Pig",
    "Pigeon",
    "Polar bear",
    "Porcupine",
    "Quail",
    "Rabbit",
    "Raccoon",
    "Rat",
    "Rattlesnake",
    "Raven",
    "Rooster",
    "Sea lion",
    "Sheep",
    "Shrew",
    "Skunk",
    "Snail",
    "Snake",
    "Spider",
    "Tiger",
    "Walrus",
    "Whale",
    "Wolf",
    "Zebra"
]

Random(bytes('Nawiasem mówiąc: przedmioty są bezbarwne',
       encoding='utf-8')).shuffle(WORDS)
