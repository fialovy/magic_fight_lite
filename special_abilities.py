import copy
import json
import random
import sys
import time

from character import Character, CharacterMagicInfo
from game_macros import CHARACTERS_DIR, DEFAULT_SPECIAL_ABILITY_TURNS, did_it_happen


class SpecialAbility:
    def __init__(self, player, opponent, effect):
        self.player = player
        self.opponent = opponent
        # literally just load them all from here for now
        self.effect_func = getattr(sys.modules[__name__], effect)

    def perform(self, **additional_options):
        return self.effect_func(self.player, self.opponent, **additional_options)


def _shapeshift(
    player,
    name,
    special_namepath=None,
    article="",
):
    player.life -= 1

    shapeshifted = Character(name=name, special_namepath=special_namepath)
    shapeshifted.life = player.life

    print(f"{player.name} becomes{' ' if article else ''}{article} {name}!")
    time.sleep(1)

    return shapeshifted


def change_to_norm(player, opponent, **_):
    norm = _shapeshift(player, "Norm", special_namepath=f"{CHARACTERS_DIR}/nora/norm")
    return norm, opponent


def change_to_nora(player, opponent, **_):
    nora = _shapeshift(player, "Nora")
    return nora, opponent


# TODO: if computer takes on this form, give it an easy out so it doesn't bore people
def change_to_meadow_sprite(player, opponent, **_):
    meadow_sprite = _shapeshift(
        player,
        "Meadow Sprite",
        special_namepath=f"{CHARACTERS_DIR}/nora/meadow_sprite",
        article="a",
    )
    return meadow_sprite, opponent


def _potion_life_effect():
    """Return a positive or negative integer value to add to poor,
    drunken character's current life value.
    """
    sign = -1 if did_it_happen() else 1
    return sign * random.choice(range(1, 6))


def _drunkify_string_list(strings):
    return list(map(lambda string: "".join(reversed(string)), strings))


def _drunkify_spells(magic_info):
    """Flip the given spell descriptions upside down, because we are drunk."""
    drunken_magic = copy.deepcopy(magic_info)  # it's not THAT big
    for dimension_info in drunken_magic["deals"].values():
        dimension_info["spells"] = _drunkify_string_list(dimension_info["spells"])
    return drunken_magic


def _print_potion_effect(character_name, effect):
    positive_effect = effect > 0
    condrunktion = "and" if positive_effect else "but"
    action = "gives" if positive_effect else "costs"

    commentary = (
        "That's some good stuff" if positive_effect else f"Poor {character_name}."
    )
    print(
        f"{character_name} gets drunk, {condrunktion} this time it {action} "
        f"{abs(effect)} life points! {commentary}.\n"
    )
    time.sleep(1)


def potionify(player, opponent, **_):
    effect = _potion_life_effect()
    player.life += effect

    drunkard = Character(name=player.name)
    drunkard.life = player.life
    drunkard.magic_info = _drunkify_spells(drunkard.magic_info)

    if drunkard.taunts is not None:
        drunkard.taunts["taunts"] = _drunkify_string_list(drunkard.taunts["taunts"])

    if drunkard.reactions is not None:
        drunkard.reactions["reactions"] = _drunkify_string_list(
            drunkard.reactions["reactions"]
        )

    drunkard._set_special_abilities(
        special_path=f"{drunkard.namepath}/drunk_special.json"
    )
    _print_potion_effect(drunkard.name, effect)

    return drunkard, opponent


def attempt_sobering(player, opponent, is_computer=False, **_):
    """was it a good idea?"""
    if did_it_happen():
        # Restore defaults!
        sober = Character(name=player.name)
        sober.life = player.life + 1

        if not is_computer:
            print("It worked! You have magically sobered up and gained 1 life point!\n")
        else:
            print(f"{player.name} has sobered up and gained 1 life point!\n")
        time.sleep(1)
        return sober, opponent
    else:
        player.life -= 1
        if not is_computer:
            print(
                f"There is no shortcut to sobriety, {player.name}. But this crappy "
                f"concoction did manage to take a life point from you.\n"
            )
        else:
            print(
                f"{player.name} is learning the hard way that there is no "
                f"shortcut to sobriety. They lose 1 life point!\n"
            )
        time.sleep(1)
        return player, opponent


def orbs_of_disorderify(player, opponent, is_computer=False, **_):
    """
    Mix up the hit values of the opponent's spells.
    """
    deal_amounts = [dim["amount"] for dim in opponent.magic_info["deals"].values()]

    for dimension_info in opponent.magic_info["deals"].values():
        now_deals = deal_amounts.pop(random.randrange(len(deal_amounts)))
        dimension_info["amount"] = now_deals

    opponent.affected_by_character_turns_left[player] = DEFAULT_SPECIAL_ABILITY_TURNS
    if is_computer:
        print(
            f"{player.name} has used the Orbs of Disorder to randomly "
            f"swap the hit values of your spells! Be careful! ✨🔵 ✨🟡\n"
        )

    return player, opponent
