import oci
import sys
from config import config
from InquirerPy import inquirer
from dotenv import load_dotenv
from InquirerPy import inquirer
from oci_helpers import get_groups_list
from config import config, GREEN, YELLOW, RED, RESET, STYLE
from inquire_managment import inquire_display_dict
from compartiment import compartment_selection

load_dotenv()

EXIT_OPTION = "exit"

def listing_policies(identity_client, selected_group_id):
    print(selected_group_id)
    list_policies_response = identity_client.list_policies(
        compartment_id=config["compartment_id"],
        sort_by="NAME",
        sort_order="ASC",
        lifecycle_state="ACTIVE"
    )

    # Get the data from response
    print(list_policies_response.data)

def policy_management(identity_client, raw_groups_list, config_file) -> None:
    try:
        structured_groupe_dict = get_groups_list(raw_groups_list)
        compartment_selection(identity_client, config_file)
        if not structured_groupe_dict:
            raise ValueError(f"{RED}groups not created or not found{RESET}")

        structured_groupe_dict.update({EXIT_OPTION: EXIT_OPTION})
        selected_group_name = inquire_display_dict(
            structured_groupe_dict,
            "Which group do you need ?")
        if selected_group_name == EXIT_OPTION:
            print(f"{RED}exit program ... {RESET}")
            sys.exit(0)
        listing_policies(identity_client, selected_group_name)
        # selected_compartment_credential = list_compartments[selected_compartment_name]
        # config_file["parent_compartment_id"] = selected_compartment_credential["cmp_ocid"]
        # create_new_compartment(identity_client)
    except Exception as e:
        print(f"Exception in compartment management: {e}")
