from __future__ import annotations

import oci
import datetime
from dotenv import load_dotenv
from InquirerPy import inquirer
from config import config, GREEN, YELLOW, RED, RESET, STYLE
from inquire_managment import get_compartment_list
from inquire_managment import inquire_display_dict

load_dotenv()

config_oci = config

def define_tags() -> tuple[dict, dict]:
    cmp_tag, project_tag, env_tag = config_oci["compartment_name"].split("-")
    freeform_tags = {
        'env': env_tag,
        'team': 'devops',
        'project': project_tag,
        'created_by': config_oci["username"],
        'backup-required': "false" if env_tag == "dev" else "true"
    }

    defined_tags = {
        'Oracle-Tags': {
            'CreatedBy': config_oci["username"],
            'CreatedOn': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    }

    return freeform_tags, defined_tags

def resume_compartment_data(description: str, freeform_tags, defined_tags) -> None:
    print(f"\n{YELLOW}=== Compartment Configuration ==={RESET}\n"
          f"{YELLOW}Parent compartment:{RESET} {GREEN}{config_oci['parent_compartment_name']}{RESET} → {GREEN}{config_oci['parent_compartment_id']}{RESET}\n"
          f"{YELLOW}Compartment name:{RESET} {GREEN}{config_oci['compartment_name']}{RESET}\n"
          f"{YELLOW}Description:{RESET} {GREEN}{description}{RESET}\n"
          f"{YELLOW}Freeform tags:{RESET} {GREEN}{freeform_tags}{RESET}\n"
          f"{YELLOW}Defined tags:{RESET} {GREEN}{defined_tags}{RESET}\n"
          f"{YELLOW}{'='*35}{RESET}\n")

def compartment_requirements() -> tuple[str, str]:
    # Name validation
    compartment_name = inquirer.text(
        message="Enter the compartment name:",
        style=STYLE,
        validate=lambda result: len(result.split("-")) == 3,
        invalid_message="Invalid format, use 'cmp-name-env' (ex: cmp-educhat-dev)",
    ).execute()

    # Parent compartment verification (retry loop)
    while compartment_name == config_oci["parent_compartment_name"]:
        print(f"❌ '{compartment_name}' is the same as parent. Please use a different name.")
        compartment_name = inquirer.text(
            message="Enter a NEW compartment name:",
            style=STYLE
        ).execute()

    # Description Validation
    compartment_description = inquirer.text(
        message="Enter the compartment description:",
        style=STYLE,
        validate=lambda result: 0 < len(result) <= 400,
        invalid_message="Description must be between 1 and 400 chars"
    ).execute()

    return compartment_name, compartment_description

def create_new_compartment(identity_client: oci.identity.IdentityClient) -> None:
    try:
        config_oci["compartment_name"], description = compartment_requirements()
        freeform_tags, defined_tags = define_tags()
        while True:
            resume_compartment_data(description, freeform_tags, defined_tags)
            choice = inquirer.text(
                message="do you want to create this new compartment: Y/n",
                style=STYLE,
                validate=lambda result: result == "Y" or result == "n",
                invalid_message="Please enter Y/N",
            ).execute()
            if choice == "Y":
                identity_client.create_compartment(
                    create_compartment_details=oci.identity.models.CreateCompartmentDetails(
                        compartment_id=config_oci["parent_compartment_id"],
                        name=config_oci["compartment_name"],
                        description=description,
                        freeform_tags=freeform_tags,
                        defined_tags=defined_tags
                    ))

                print(f"{GREEN}compartment management has been created{RESET}")
                break
            elif choice == "n":
                field = inquirer.text(
                    message="What to modify? (name/description) or nothing for exit: ",
                    style=STYLE,
                    validate=lambda result: result == "name" or result == "description" or result == "",
                    invalid_message="Please fill: name or description if want to exit touch enter",
                ).execute()
                if field == "name":
                    config_oci['compartment_name'] = input("New name: ").strip()
                    freeform_tags, defined_tags = define_tags()
                elif field == "description":
                    description = input(f"\n{YELLOW}New description: {RESET}").strip()
                else:
                    print(f"\n{RED}exit the programme{RESET}")
                    return
            else:
                print("❌ Choix invalide")
    except oci.exceptions.ConfigFileNotFound as e:
        raise
    except oci.exceptions.ClientError as e:
        raise
    except oci.exceptions.ConnectTimeout as e:
        raise
    except Exception as e:
        print(f"Error in create_compartment: {e}")

#{
#   'user_name': 'vincentRevole@admindev.com',
#   'user_id': 'c00cae...',
#   'user_ocid': 'ocid1.user.oc1..aaaaaaaa...',
#   'groups': [{
#       'group_name': 'Grp-DevOps-Admin',
#       'group_id': '83038...f',
#       'ocid': 'ocid1.group.oc1..aaaaaaaa...'
#    }]
#}
def compartment_management(identity_client, config_file) -> None:
    try:
        all_compartments = {}

        list_compartments = get_compartment_list(
            identity_client,
            config_file["oci_config"]["tenancy"],
            "dk_company",
            all_compartments
        )
        if not list_compartments:
            raise ValueError(f"{RED}compartment not created or not found{RESET}")

        selected_compartment_name = inquire_display_dict(list_compartments, "Which compartment do you need ?")
        selected_compartment_credential = list_compartments[selected_compartment_name]
        config_file["parent_compartment_id"] = selected_compartment_credential["cmp_ocid"]
        create_new_compartment(identity_client)
    except Exception as e:
        print(f"Exception in compartment management: {e}")
