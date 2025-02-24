import json
import os
import random
import time

from character import Character
from game_macros import (
    CHARACTERS_DIR,
    OPPONENT_SPECIAL_ABILITY_CHANCE,
    SpecialChoice,
    SpellChoice,
    confirm_input_choice,
    did_it_happen,
    get_input_choice,
)
from special_abilities import SpecialAbility


class Game:
    def __init__(self):
        self.player = None
        self.opponent = None
        self.all_characters = {}

        for name in os.listdir(f"{CHARACTERS_DIR}"):
            character = Character(name=name.title())
            self.all_characters[name] = character

    def select_character(self, prompt="Press a key to choose a character:\n"):
        chosen_input = get_input_choice(
            prompt=prompt,
            choices=self.all_characters,
            capitalize_choice=True,
            offer_random_choice=True,
        )
        chosen_confirmed = confirm_input_choice(
            choice=chosen_input,
            prompt=f"{self.all_characters[chosen_input].ascii_art}\n\n{self.all_characters[chosen_input].bio}\n",
            deny_func=self.select_character,
            deny_func_kwargs={"prompt": prompt},
        )

        return chosen_confirmed

    def _construct_player_spell_choices(
        self,
    ):
        """During a player's turn, construct a varying list of spell choices
        based on what is available in the character JSON.

        Return dict that is still useful to us in terms of hits.
        """
        choices = {}

        for dimension, dimension_info in self.player.magic_info["deals"].items():
            # Not everyone can do every kind of magic, which means they
            # might be better at fewer things.
            if not dimension_info["spells"]:
                continue
            # Rotate among the available spells for each dimension
            choice_key = f'{random.choice(dimension_info["spells"])} ({dimension})'
            choices[choice_key] = SpellChoice(
                dimension=dimension, hit=dimension_info["amount"]
            )

        for ability_name, ability_info in self.player.special_abilities_info.items():
            choices[ability_name] = SpecialChoice(
                description=ability_info["description"], effect=ability_info["effect"]
            )

        return choices

    def hit(self, whom, dimension, max_hit):
        """Hit character (player or opponent) with up to the amount of given
        dimension's magic they take.
        """
        hit = min(whom.magic_info["takes"][dimension]["amount"], max_hit)
        whom.life -= hit
        print(f"{whom.name} takes {hit} {dimension} damage!\n")
        time.sleep(1)

    def wear_down_existing_effects(self, affected, is_computer=False):
        # if 0, do nothing
        # if 1, reset magic infos (e.g., if affected by Orbs of Disorder, regular magic is restored
        # if >= 1, decrement
        # right now this is kinda silly because there is one opponent at a time,
        # and when that one opponent's effect wears off, 'everyone's' does
        # but who knows...maybe there will be a future
        for character, turns_left in affected.affected_by_character_turns_left.items():
            if turns_left == 0:
                continue

            if turns_left == 1:
                affected.reset(opponent_name=character.name, is_computer=is_computer)

            affected.affected_by_character_turns_left[character] -= 1

        return affected

    def player_turn(self):
        spell_infos = self._construct_player_spell_choices()
        spell = get_input_choice(
            prompt="\nChoose your spell:\n",
            choices=spell_infos,
            capitalize_choice=False,
        )
        choice = spell_infos[spell]

        if isinstance(choice, SpellChoice):
            dimension, max_hit = choice.dimension, choice.hit
            self.hit(self.opponent, dimension, max_hit)
            self.opponent.possibly_react()

        elif isinstance(choice, SpecialChoice):
            description, effect = choice.description, choice.effect
            special_confirmed = confirm_input_choice(
                choice=spell,
                prompt=description,
                deny_func=self.player_turn,
            )
            if special_confirmed in self.player.special_abilities_info:
                ability = SpecialAbility(
                    player=self.player, opponent=self.opponent, effect=choice.effect
                )
                self.player, self.opponent = ability.perform()

        self.player = self.wear_down_existing_effects(self.player, is_computer=False)

    def opponent_turn(self):
        self.opponent.possibly_taunt()

        if self.opponent.special_abilities_info and did_it_happen(
            OPPONENT_SPECIAL_ABILITY_CHANCE
        ):
            special_ability = SpecialAbility(
                player=self.opponent,
                opponent=self.player,
                effect=random.choice(
                    [
                        info["effect"]
                        for info in self.opponent.special_abilities_info.values()
                    ]
                ),
            )
            # The opponent of the opponent is of course the player, let's be super
            # clear about player, opponent result format returned by perform()
            (
                modified_opponent_as_player,
                modified_player_as_opponent,
            ) = special_ability.perform(is_computer=True)
            self.opponent, self.player = (
                modified_opponent_as_player,
                modified_player_as_opponent,
            )
        # If the opponent does not activate a special ability, they just choose a spell:
        else:
            spell_info = self.opponent.magic_info["deals"]
            # Recall that not everyone can deal every kind, as a cost to being
            # super strong in some.
            able_dimensions = [
                dim for dim, info in spell_info.items() if info["spells"]
            ]
            dimension = random.choice(able_dimensions)
            spell = random.choice(spell_info[dimension]["spells"])

            print(f'{self.opponent.name} chooses: "{spell}"\n')
            time.sleep(1)
            self.hit(self.player, dimension, max_hit=spell_info[dimension]["amount"])

        self.opponent = self.wear_down_existing_effects(self.opponent, is_computer=True)

    def play(self):
        player_choice = self.select_character()
        self.player = self.all_characters[player_choice]
        # You cannot be your own opponent (not even you, Adrian).
        del self.all_characters[player_choice]

        opponent_choice = self.select_character(
            prompt="Press a key to choose your opponent:\n"
        )
        self.opponent = self.all_characters[opponent_choice]

        print(f"\n{self.opponent.name} is ready to duel!\n")
        time.sleep(1)
        print("Ready?\n")
        time.sleep(2)

        # well it is a start
        while True:
            self.player.print_life()
            self.opponent.print_life()
            time.sleep(1)

            self.player_turn()
            if self.opponent.life <= 0:
                print(
                    f"You have defeated {self.opponent.name}! Congratulations, Sorcerer."
                )
                time.sleep(2)
                return

            self.opponent_turn()
            if self.player.life <= 0:
                print(f"{self.opponent.name} has bested you. Game over.")
                time.sleep(2)
                return
