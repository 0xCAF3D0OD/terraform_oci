from __future__ import annotations

import sys

import oci
import datetime
from dotenv import load_dotenv
from InquirerPy import inquirer
from config import config, GREEN, YELLOW, RED, RESET, STYLE
from inquire_managment import inquire_display_dict
from oci_helpers import get_compartment_list

load_dotenv()

config_oci = config
EXIT_OPTION = "exit"

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

def compartment_selection(identity_client: oci.identity.IdentityClient, config_file: dict) -> None:
    all_compartments = {}

    list_compartments = get_compartment_list(
        identity_client,
        config_file["oci_config"]["tenancy"],
        "dk_company",
        all_compartments
    )
    if not list_compartments:
        raise ValueError(f"{RED}compartment not created or not found{RESET}")

    list_compartments.update({EXIT_OPTION: EXIT_OPTION})
    selected_compartment_name = inquire_display_dict(
        list_compartments,
        "Which compartment do you need ?")
    if selected_compartment_name == EXIT_OPTION:
        print(f"{RED}exit program ... {RESET}")
        sys.exit(0)
    selected_compartment_credential = list_compartments[selected_compartment_name]
    config_file["parent_compartment_id"] = selected_compartment_credential["cmp_ocid"]
    config_file["compartment_id"] = selected_compartment_credential["cmp_ocid"]

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
        compartment_selection(identity_client, config_file)
        create_new_compartment(identity_client)

    except oci.exceptions.ServiceError as e:
        # Erreurs retournées par l'API Oracle (ex: 403 Forbidden, 404 Not Found)
        print(f"❌ OCI Service Error: status={e.status}, code={e.code}, message={e.message}")

    except oci.exceptions.RequestException as e:
        # Erreurs de connexion (ex: Timeout, pas d'internet)
        print(f"📡 Network Error: Impossible de contacter les serveurs OCI. Vérifiez votre connexion.")

    except KeyError as e:
        # Erreur si le fichier config ou le dictionnaire est mal formé
        print(f"🔑 Configuration Error: La clé {e} est manquante dans les credentials ou la config.")

    except ValueError as e:
        # Pour ton raise ValueError personnalisé (ex: compartiment non trouvé)
        print(f"⚠️ Validation Error: {e}")

    except Exception as e:
        # Le filet de sécurité pour tout le reste
        print(f"🔥 Unexpected Error [{type(e).__name__}]: {e}")
