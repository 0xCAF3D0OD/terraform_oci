from __future__ import annotations

import os
import oci

from typing import Tuple, Any

from dotenv import load_dotenv
from inquire_managment import inquire_display_dict, inquire_display_process
from create_compartiment import compartment_management

load_dotenv()

# Codes ANSI
GREEN = "\033[1;32m"  # Bold Green (valeurs)
YELLOW = "\033[1;33m"  # Bold Yellow (labels)
RESET = "\033[0m"  # Reset

def get_domain_list() -> dict[str, str]:
    env_vars = dict(os.environ)
    oci_domains = {key: value for key, value in env_vars.items() if "DOMAIN" in key}

    return oci_domains

def get_user_list(config_file) -> dict[str, list[Any] | Any]:
    domains = get_domain_list()
    answers = inquire_display_dict(domains, "domain")
    domain_url = domains[answers]

    identity_domains_client = oci.identity_domains.IdentityDomainsClient(config_file, domain_url)
    response = identity_domains_client.list_users(attributes="userName,groups,ocid")

    user_list = {}

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
        user_list[user.user_name] = user_info
    return user_list

def main():
    try:
        while True:
            process = inquire_display_process()
            if process != "exit":
                config_file = oci.config.from_file("~/.oci/config")
                users_list = get_user_list(config_file)
                selected_user_name = inquire_display_dict(users_list, "user name")
                selected_user_credentials = users_list[selected_user_name]
                if "new compartment" in process:
                    compartment_management(selected_user_credentials)
                elif process == "new policy":
                    print(f"you have choosen the creation of a {process} with {selected_user_name}")
                elif process == "new user":
                    print(f"you have choosen the creation of a {process} with {selected_user_name}")
                elif process == "new group":
                    print(f"you have choosen the creation of a {process} with {selected_user_name}")
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