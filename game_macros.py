"""
Currently the dumping ground of constants and shared utils
"""

import random
from collections import namedtuple

## Constants

CHARACTERS_DIR = "characters"
GAME_LIFE = 15
OPPONENT_SPECIAL_ABILITY_CHANCE = 0.2
DEFAULT_SPECIAL_ABILITY_TURNS = (
    3  # number of turns a special ability lasts by default, if it affects any state
)


## In the original magic_fight, there would be all these nice type definitions here.
## but now...at least you don't have to install mypy. Or literally anything.
## ...that's the hope...

## ...anyway, next comes: General helper utils


def did_it_happen(chance=0.5):
    """Helper for all kinds of things that occur at a given chance between
    0 and 1.
    """
    return 100 * chance > random.randint(0, 100)


def get_input_choice(
    prompt,
    choices,
    capitalize_choice=True,
    offer_random_choice=False,
):
    """Given a custom prompt and list of text choices, prompt user to
    make a choice, and insist that they do so correctly until a proper
    one can be returned.
    """
    input_choices = dict(enumerate(choices))
    random_choice_index = len(choices)
    if offer_random_choice:
        input_choices[random_choice_index] = "Choose for me! 🔮"

    choice = None
    while choice is None:
        print(prompt)
        for idx, item in input_choices.items():
            print(f"{idx}: {item.title() if capitalize_choice else item}\n")

        choice_input = input(">>> ")
        try:
            choice = int(choice_input.strip())
        except Exception:
            print("Please choose a number in the given range.")
            choice = None
            continue

        # ...but the enum made this 'interface' easy to validate.
        if choice not in input_choices:
            print("Please choose a number in the given range.")
            choice = None

    if choice == random_choice_index and offer_random_choice:
        del input_choices[random_choice_index]
        return random.choice(list(input_choices.values()))

    return input_choices[choice]


def confirm_input_choice(
    choice,
    prompt,
    deny_func,
    deny_func_kwargs=None,
):
    """Print prompt presumably associated with some choice
    (e.g., info about a chosen character), and ask for y/n confirmation.

    Call given deny_func to custom 'reset' if they do not confirm.
    """
    deny_func_kwargs = deny_func_kwargs or {}
    confirmed_choice = None

    while confirmed_choice is None:
        print(prompt)
        print(f"Confirm choice? Type y or n.")

        confirm = input(">>> ")
        try:
            confirm = confirm.strip().lower()
        except Exception:
            print('Please type "y" or "n"')
            continue

        if confirm == "y":
            confirmed_choice = choice
        elif confirm == "n":
            return deny_func(**deny_func_kwargs)
        else:
            print('Please type "y" or "n"')
            continue

    return confirmed_choice
