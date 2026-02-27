import oci
from oci.config import from_file
import datetime
from dotenv import load_dotenv

load_dotenv()
from rich.console import Console
from rich.table import Table
import os

config = {
    "oci_config": {},
    "username": "",
    "tenancy_ocid": None,
    "compartment_name": "",
    "parent_compartment_id": None,
    "parent_compartment_name": ""
}

def select_from_list_rich(items: list, prompt: str = "Select an option") -> str:
    console = Console()

    table = Table(title=prompt)
    table.add_column("Option", style="cyan")
    table.add_column("Index", style="yellow")

    for i, item in enumerate(items, 1):
        table.add_row(item, str(i))

    console.print(table)

    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except ValueError:
            pass
        console.print("[red]Invalid input[/red]")

def define_tags() -> tuple[dict, dict]:
    cmp_tag, project_tag, env_tag = config["compartment_name"].split("-")
    freeform_tags = {
        'env': env_tag,
        'team': 'devops',
        'project': project_tag,
        'created_by': config["username"],
        "backup-required": "false" if env_tag == "dev" else "true"
    }

    defined_tags = {
        'Oracle-Tags': {
            'CreatedBy': config["username"],
            'Environment': env_tag,
            "CreatedOn": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    }

    return freeform_tags, defined_tags

def resume_compartment_data(description: str, freeform_tags, defined_tags) -> None:
    # Codes ANSI
    GREEN = "\033[1;32m"    # Bold Green (valeurs)
    YELLOW = "\033[1;33m"   # Bold Yellow (labels)
    RESET = "\033[0m"       # Reset

    print(f"\n{YELLOW}=== Compartment Configuration ==={RESET}\n"
          f"{YELLOW}Parent compartment:{RESET} {GREEN}{config['parent_compartment_name']}{RESET} → {GREEN}{config['parent_compartment_id']}{RESET}\n"
          f"{YELLOW}Compartment name:{RESET} {GREEN}{config['compartment_name']}{RESET}\n"
          f"{YELLOW}Description:{RESET} {GREEN}{description}{RESET}\n"
          f"{YELLOW}Freeform tags:{RESET} {GREEN}{freeform_tags}{RESET}\n"
          f"{YELLOW}Defined tags:{RESET} {GREEN}{defined_tags}{RESET}\n"
          f"{YELLOW}{'='*35}{RESET}\n")

def compartment_requirements() -> tuple[str, str]:
    compartment_name = input("compartment_name: ")
    if compartment_name == config["parent_compartment_name"]:
        print("compartment_name already exists, retry")
        compartment_name = input("compartment_name: ")
    compartment_description = input("compartment_description: ")
    if compartment_name == "" or compartment_description == "":
        raise ValueError('please input compartment_name and compartment_description')
    elif len(compartment_name) > 100 or len(compartment_description) > 400:
        raise ValueError("please be sure to be less than 100 characters for compartment_name and "
                         "400 for compartment_description")
    return compartment_name, compartment_description

def create_compartment(identity_client: oci.identity.IdentityClient) -> None:
    try:
        config["compartment_name"], description = compartment_requirements()
        freeform_tags, defined_tags = define_tags()
        while True:

            resume_compartment_data(description, freeform_tags, defined_tags)

            choice = input("do you want to create this new compartment: Y/n: ")
            if choice == "Y":
                create_compartment_response = identity_client.create_compartment(
                    create_compartment_details=oci.identity.models.CreateCompartmentDetails(
                        compartment_id=config["parent_compartment_id"],
                        name=config["compartment_name"],
                        description=description,
                        freeform_tags=freeform_tags,
                        defined_tags=defined_tags
                    ))
                print(create_compartment_response.data)
                break
            elif choice == "n":
                field = input("What to modify? (name/description) or nothing for exit: ").strip().lower()
                if field == "name":
                    config['compartment_name'] = input("New name: ").strip()
                    freeform_tags, defined_tags = define_tags()
                elif field == "description":
                    description = input("New description: ").strip()
                else:
                    print("exit the programme")
                    return
            else:
                print("❌ Choix invalide")
    except oci.exceptions.ConfigFileNotFound as e:
        print(f'OCI ERROR Config file not found: {e}')
    except oci.exceptions.ClientError as e:
        print(f"OCI ERROR client error: {e}")
    except oci.exceptions.ConnectTimeout as e:
        print(f"OCI ERROR timeout: {e}")
    except Exception as e:
        print(f"Error in create_compartment: {e}")


def compartment_management(identity_client: oci.identity.IdentityClient) -> None:
    try:
        config["parent_compartment_name"] = input("parent_compartment_name: ")
        if config["parent_compartment_name"] == "":
            raise ValueError("please input parent_compartment_name")

        list_compartments_response = identity_client.list_compartments(
            compartment_id=config["tenancy_ocid"],
            name=config["parent_compartment_name"],
            sort_by="NAME",
            sort_order="ASC",
            lifecycle_state="ACTIVE"
        )

        if not list_compartments_response.data:
            raise ValueError("compartment not created or not found")
        elif len(list_compartments_response.data) == 1:
            print("Creating compartment...")
            config["parent_compartment_id"] = list_compartments_response.data[0].id
            print(f'compartment_parent: {config["parent_compartment_id"]}')
            create_compartment(identity_client)
    except Exception as e:
        print(f"Exception in compartment management: {e}")

def get_user_list() -> None:
    config_file = oci.config.from_file("~/.oci/config")

    # 2. Définir l'endpoint spécifique de votre domaine d'identité
    domain_endpoint = "https://idcs-d587d08168504829a27dc33538d4cbe3.identity.oraclecloud.com:443"

    # 3. Initialiser le client IdentityDomains avec l'endpoint
    identity_domains_client = oci.identity_domains.IdentityDomainsClient(config_file, domain_endpoint)

    # 4. Lister les utilisateurs du domaine
    # Note : les résultats sont dans .data.resources pour ce client
    response = identity_domains_client.list_users()

    for user in response.data.resources:
        # Équivalent du grep "name" (affiche le nom d'affichage ou le login)
        print(f"User Name: {user.user_name} | Display Name: {user.display_name}")

def main():
    try:
        while True:
            choice = input("do you want to create compartment: Y/n: ")
            if choice == "Y":
                get_user_list()
                # config["username"] = input("enter required username for compartment creation: ")
                # if config["username"] == "":
                #     raise ValueError("please input username for compartment creation")
                # select_from_list_rich()
                # config["oci_config"] = from_file("~/.oci/config", config["username"])
                # identity_client = oci.identity.IdentityClient(config["oci_config"])
                # tenancy = identity_client.get_tenancy(config["oci_config"]["tenancy"]).data
                # config["tenancy_ocid"] = tenancy.id
                #
                # compartment_management(identity_client)
                break
            elif choice == "n":
                print("break process...")
                break
            else:
                print("please input Y/n")
    except Exception as e:
        print(f"Exception in main: {e}")


if __name__ == "__main__":
    main()