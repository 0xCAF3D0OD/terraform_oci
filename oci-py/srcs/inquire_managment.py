from __future__ import annotations
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.utils import get_style
from config import STYLE
from typing import Any
import oci

def inquire_display_dict(dictionary: dict[str, str], key_phrase: str) -> Any:
    # Syntaxe InquirerPy : plus besoin de créer une liste de dictionnaires
    choice = inquirer.select(
        message=f"{key_phrase}",
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

def get_compartment_list(identity_client, current_id, parent_name, list_compartments) -> dict:
    try:
        # Appel API
        list_compartments_response = identity_client.list_compartments(
            compartment_id=current_id,
            sort_by="NAME",
            sort_order="ASC",
            lifecycle_state="ACTIVE"
        )

        for compartment in list_compartments_response.data:
            # On crée un label unique pour éviter d'écraser des doublons (Nom + Parent)
            display_label = f"{compartment.name} (parent: {parent_name})"

            list_compartments[display_label] = {
                "cmp_name": compartment.name,
                "cmp_parent": parent_name,
                "cmp_ocid": compartment.id,
            }
            get_compartment_list(identity_client, compartment.id, compartment.name, list_compartments)

        return list_compartments

    except oci.exceptions.ServiceError as e:
        # Erreur côté OCI (ex: 403 Forbidden si tu n'as pas accès à un sous-compartiment)
        print(f"⚠️  Skipping sub-compartments of {parent_name}: {e.message}")
        return list_compartments
    except Exception as e:
        # Erreur critique (ex: Coupure réseau)
        print(f"❌ Critical error fetching compartments: {e}")
        return list_compartments