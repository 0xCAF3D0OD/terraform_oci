from __future__ import annotations
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from config import STYLE
from typing import Any
import oci
import os

def inquire_display_dict(dictionary: dict[str, str], key_phrase: str) -> Any:
    choice = inquirer.select(
        message=f"{key_phrase}",
        style=STYLE,  # On applique le style ici
        choices=list(dictionary.keys()),
    ).execute()  # .execute() remplace inquirer.prompt()

    # On retourne un dictionnaire pour rester cohérent avec tes appels précédents
    return choice


def inquire_display_user_actions() -> Any:
    user_action = [
        "1. -- exit",
        Separator(),
        "2A. -- new compartment",
        # "2B. -- delete compartment",
        Separator(),
        "3A. -- new policy",
        # "3B. -- delete policy",
        # Separator(),
        # "4A. -- new user",
        # "4B. -- delete user",
        # Separator(),
        # "5A. -- new group",
        # "5B. -- delete group"
    ]

    choice = inquirer.select(
        message=f"Which process do you need ?",
        style=STYLE,
        choices=user_action,
        pointer="👉",
    ).execute()

    return choice

def inquirer_oci_domains() -> str:
    env_vars = dict(os.environ)
    oci_domains = {key: value for key, value in env_vars.items() if "DOMAIN" in key}

    answers = inquire_display_dict(oci_domains, "Which domain do you need ?")
    domain_url = oci_domains[answers]

    return domain_url

def inquirer_oci_users(config_file) -> tuple[dict[str, list[Any] | Any], oci.identity_domains.IdentityDomainsClient]:
    domain_url = inquirer_oci_domains()

    identity_domains_client = oci.identity_domains.IdentityDomainsClient(config_file, domain_url)
    response = identity_domains_client.list_users(attributes="userName,groups,ocid")

    users_list = {}

    for user in response.data.resources:
        user_info = {
            "user_name": user.user_name,
            "user_id": user.id,
            "user_ocid": user.ocid,
            "groups": []
        }
        if hasattr(user, 'groups') and user.groups:
            for group in user.groups:
                group_data = {
                    "group_name": group.display,
                    "group_id": group.value,
                    "ocid": group.ocid
                }
                user_info["groups"].append(group_data)
        else:
            print("  - Aucun groupe")
        users_list[user.user_name] = user_info
    selected_user_name = inquire_display_dict(users_list, "Which user do you want ?")
    selected_user_credentials = users_list[selected_user_name]
    return selected_user_credentials, identity_domains_client