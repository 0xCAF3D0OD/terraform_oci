import os
import oci

config = {
    "oci_config": {},
    "username": "",
    "tenancy_ocid": None,
    "compartment_name": "",
    "parent_compartment_id": None,
    "parent_compartment_name": ""
}

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
                config["oci_config"] = oci.config.from_file("~/.oci/config", config["username"])
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