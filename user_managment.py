from __future__ import annotations

import oci
import datetime
from dotenv import load_dotenv
from typing import Tuple, Any
import inquirer
from create_compartiment import creating_compartment
load_dotenv()
from rich.console import Console
from rich.table import Table
import os

# Codes ANSI
GREEN = "\033[1;32m"  # Bold Green (valeurs)
YELLOW = "\033[1;33m"  # Bold Yellow (labels)
RESET = "\033[0m"  # Reset

def get_domain_list() -> dict[str, str]:
    env_vars = dict(os.environ)
    oci_domains = {key: value for key, value in env_vars.items() if "DOMAIN" in key}

    return oci_domains

def inquire_display_dict(dictionary: dict[str, str], key_word: str) ->  dict[Any, Any] | None | Any:
    questions = [
        inquirer.List(f'{key_word}',
                      message=f"{YELLOW}What {key_word} do you need ?{RESET}",
                      choices=[key for key in dictionary.keys() if not None],
                      ),
    ]
    answers = inquirer.prompt(questions)
    print(f"{GREEN}you have choosen {answers[f'{key_word}']}{RESET}\n")
    return answers

def get_user_list(config_file) -> dict[str, list[Any] | Any]:
    domains = get_domain_list()
    answers = inquire_display_dict(domains, "domain")
    domain_url = domains[answers["domain"]]

    identity_domains_client = oci.identity_domains.IdentityDomainsClient(config_file, domain_url)
    response = identity_domains_client.list_users(attributes="userName,groups,ocid")

    user_list = {}

    for user in response.data.resources:
        user_info = {
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
        user_list[user.user_name] = user_info
    return user_list

def inquire_display_process() ->  dict[Any, Any] | None | Any:
    list_process = ["exit", "new compartment", "new policy", "new user", "new group"]
    questions = [
        inquirer.List('process',
                      message=f"{YELLOW}What process do you need ?{RESET}",
                      choices=list_process,
                      ),
    ]
    answers = inquirer.prompt(questions)
    print(f"{GREEN}you have choosen {answers['process']}{RESET}\n")
    return answers['process']

def main():
    try:
        while True:
            process = inquire_display_process()
            if process != "exit":
                config_file = oci.config.from_file("~/.oci/config")
                users_list = get_user_list(config_file)
                user_credential = inquire_display_dict(users_list, "user name")
                if process == "new compartment":
                    print(f"you have choosen the creation of a {process} with {user_credential['user name']}")
                    creating_compartment(user_credential)
                elif process == "new policy":
                    print(f"you have choosen the creation of a {process} with {user_credential['user name']}")
                elif process == "new user":
                    print(f"you have choosen the creation of a {process} with {user_credential['user name']}")
                elif process == "new group":
                    print(f"you have choosen the creation of a {process} with {user_credential['user name']}")
                break
            elif process == "exit":
                print("break process...")
                break
            else:
                print("please input Y/n")
    except Exception as e:
        print(f"Exception in main: {e}")


if __name__ == "__main__":
    main()