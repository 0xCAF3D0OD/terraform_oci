from __future__ import annotations
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.utils import get_style
from typing import Any

# Codes ANSI
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

STYLE = get_style({
        "questionmark": "#e5c07b",
        "message": "#e5c07b bold",
        "pointer": "#61afef bold",
        "answermark": "#98c379",
        "answer": "#98c379 bold",
    },
    style_override=False) # style_override=False permet de garder les couleurs de base pour le reste

def inquire_display_dict(dictionary: dict[str, str], key_word: str) -> Any:
    # Syntaxe InquirerPy : plus besoin de créer une liste de dictionnaires
    choice = inquirer.select(
        message=f"Which {key_word} do you need ?",
        style=STYLE,  # On applique le style ici
        choices=list(dictionary.keys()),
    ).execute()  # .execute() remplace inquirer.prompt()

    # On retourne un dictionnaire pour rester cohérent avec tes appels précédents
    return choice


def inquire_display_process() -> Any:
    list_process = [
        "1. -- exit",
        Separator(),  # Utilisation de l'objet Separator
        "2A. -- new compartment",
        "2B. -- delete compartment",
        Separator(),
        "3A. -- new policy",
        "3B. -- delete policy",
        Separator(),
        "4A. -- new user",
        "4B. -- delete user",
        Separator(),
        "5A. -- new group",
        "5B. -- delete group"
    ]

    choice = inquirer.select(
        message=f"Which process do you need ?",
        style=STYLE,
        choices=list_process,
        pointer="👉",  # Petit bonus visuel sympa
    ).execute()

    return choice

def get_compartment_list(identity_client, config, parent_cmp, list_compartments) -> Any:

    list_compartments_response = identity_client.list_compartments(
        compartment_id=config,
        sort_by="NAME",
        sort_order="ASC",
        lifecycle_state="ACTIVE"
    )
    for compartment in list_compartments_response.data:
        list_compartments[compartment.name] = {
            "cmp_parent": parent_cmp,
            "cmp_name": compartment.name,
            "cmp_tenancy_id": compartment.compartment_id,
            "cmp_ocid": compartment.id,
        }
        get_compartment_list(identity_client, compartment.id, list_compartments[compartment.name], list_compartments)

    return list_compartments