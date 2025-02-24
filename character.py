import json
import os
import random
import time

from game_macros import (
    CHARACTERS_DIR,
    GAME_LIFE,
    SpecialChoice,
    SpellChoice,
    did_it_happen,
)


class Character:
    def __init__(self, name, special_namepath=None):
        # amount of juice left
        self.life = GAME_LIFE
        self.name = name
        # how to get to the files (because shapeshifters)
        self.namepath = special_namepath or f"{CHARACTERS_DIR}/{name.lower()}"
        # countdown of turns left by character causing effect. naming is hard.
        self.affected_by_character_turns_left = {}

        # a short description of the character
        self._set_bio()
        # this game has ✨ advanced graphics ✨
        self._set_ascii_art()
        self._set_magic_info()
        self._set_taunts()
        self._set_reactions()
        self._set_special_abilities()

    def _set_attr_from_file(
        self,
        attr,
        filepath,
        strip=False,
        allow_empty=False,
        empty_val=None,
    ):
        """
        Read and set character data from a file, and set the character attribute
        to empty_val if file does not exist.

        If strip is true, well...do strip() to get rid of whitespace on the ends.
        """
        if os.path.exists(filepath):
            with open(filepath, "r") as attr_fl:
                if filepath.endswith("txt"):
                    val = attr_fl.read()
                    if strip:
                        val = val.strip()
                elif filepath.endswith("json"):
                    val = json.load(attr_fl)
                else:
                    raise ValueError(f"Unsupported filetype at the moment: {filepath}")
            setattr(self, attr, val)
        elif allow_empty:
            setattr(self, attr, empty_val)
        else:
            raise FileNotFoundError(
                f"Could not set {attr}! Expected file not found: {filepath}"
            )

    def _set_bio(self):
        self._set_attr_from_file(
            attr="bio",
            filepath=f"{self.namepath}/bio.txt",
            strip=True,
        )

    def _set_ascii_art(self):
        self._set_attr_from_file(
            attr="ascii_art",
            filepath=f"{self.namepath}/ascii_art.txt",
            strip=True,
            allow_empty=True,
            empty_val="",
        )

    def _set_magic_info(self):
        self._set_attr_from_file(
            attr="magic_info",
            filepath=f"{self.namepath}/magic.json",
        )

    def _set_taunts(self):
        self._set_attr_from_file(
            attr="taunts",
            filepath=f"{self.namepath}/taunts.json",
            allow_empty=True,
            empty_val=None,
        )

    def _set_reactions(self):
        self._set_attr_from_file(
            attr="reactions",
            filepath=f"{self.namepath}/reactions.json",
            allow_empty=True,
            empty_val=None,
        )

    def _set_special_abilities(self, special_path=None):
        self._set_attr_from_file(
            attr="special_abilities_info",
            filepath=special_path or f"{self.namepath}/special.json",
            allow_empty=True,
            empty_val={},
        )

    def print_life(self):
        print(f'{self.name}: {"+"*self.life}({self.life} sparks left)')

    def possibly_taunt(self):
        """Depending on their percent chance of doing so and whether they actually have taunts,
        (some characters are nicer), pick and say a random taunt.
        """
        if self.taunts is not None and did_it_happen(self.taunts["chance"]):
            print(f'{self.name} says: {random.choice(self.taunts["taunts"])}\n')
            time.sleep(1)

    def possibly_react(self):
        """If character can verbally react to a hit (some are more vocal),
        do so based on their chance.
        """
        if self.reactions is not None and did_it_happen(self.reactions["chance"]):
            print(
                f"{self.name} says: " f'{random.choice(self.reactions["reactions"])}\n'
            )
            time.sleep(1)

    def reset(self, opponent_name, is_computer=False):
        # for now broad blind reset; later more specific how (and if) based
        # on character and status of same affected areas from other characters
        self._set_magic_info()
        self._set_taunts()
        self._set_reactions()

        affected_phrase = f"{self.name} has" if is_computer else "You have"
        affector_phrase = "your" if is_computer else f"{opponent_name}'s"
        print(f"{affected_phrase} recovered from {affector_phrase} magical effect!\n")
        time.sleep(1)
