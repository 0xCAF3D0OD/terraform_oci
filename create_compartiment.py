import oci
from oci.config import from_file

config = {
    "oci_config": {},
    "username": "",
    "tenancy_ocid": None,
    "parent_compartment_id": None,
    "parent_compartment_name": None
}


# def define_tags() -> tuple[dict, dict]:
#     freeform_tags = {
#         'env': 'dev',
#         'team': 'devops',
#         'project': 'educhat'
#     }
#
#     defined_tags = {
#         'Oracle-Tags': {
#             'CreatedBy': config["username"],
#             'Environment': 'development'
#         }
#     }
#
#     return freeform_tags, defined_tags


def compartment_requirements() -> tuple[str, str]:
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
        name, description = compartment_requirements()
        # freeform_tags, defined_tags = define_tags()

        print(f"name: {name}, description: {description}")
        create_compartment_response = identity_client.create_compartment(
            create_compartment_details=oci.identity.models.CreateCompartmentDetails(
                compartment_id=config["parent_compartment_id"],
                name=name,
                description=description,
                # freeform_tags=freeform_tags,
                # defined_tags=defined_tags
            ))
        print(create_compartment_response.data)
    except oci.exceptions.ConfigFileNotFound as e:
        print(f'OCI ERROR Config file not found: {e}')
    except oci.exceptions.ClientError as e:
        print(f"OCI ERROR client error: {e}")
    except oci.exceptions.ConnectTimeout as e:
        print(f"OCI ERROR timeout: {e}")
    except Exception as e:
        print(f"Exception in create_compartment: {e}")


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


def main():
    try:
        while True:
            choice = input("do you want to create compartment: Y/n: ")
            if choice == "Y":
                config["username"] = input("enter required username for compartment creation: ")
                if config["username"] == "":
                    raise ValueError("please input username for compartment creation")

                config["oci_config"] = from_file("~/.oci/config", config["username"])
                identity_client = oci.identity.IdentityClient(config["oci_config"])
                tenancy = identity_client.get_tenancy(config["oci_config"]["tenancy"]).data
                config["tenancy_ocid"] = tenancy.id

                compartment_management(identity_client)
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