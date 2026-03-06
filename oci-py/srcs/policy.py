import oci
from InquirerPy import inquirer
from inquire_managment import get_compartment_list, inquire_display_dict

config = {
    "oci_config": {},
    "username": "",
    "tenancy_ocid": None,
    "compartment_name": "",
    "parent_compartment_id": None,
    "parent_compartment_name": ""
}
def listing_policies(identity_client, compartment_selection_id):
    list_policies_response = identity_client.list_policies(
        compartment_id=compartment_selection_id,
        sort_by="NAME",
        sort_order="ASC",
        lifecycle_state="ACTIVE")

    # Get the data from response
    print(list_policies_response.data)

def policy_management(selected_user_credentials) -> None:
    config["username"] = selected_user_credentials["user_name"]
    config["oci_config"] = oci.config.from_file("~/.oci/config", selected_user_credentials["user_name"])
    config["tenancy_ocid"] = config["oci_config"]["tenancy"]
    identity_client = oci.identity.IdentityClient(config["oci_config"])

    compartments_list = get_compartment_list(
        identity_client,
        config["tenancy_ocid"],
        "dk_company",
        {}
    )

    compartment_selection_name = inquire_display_dict(
        compartments_list,
        "which compartment you want to list the policies?")
    compartment_selection_dict_data = compartments_list[compartment_selection_name]
    listing_policies(identity_client, compartment_selection_dict_data["cmp_ocid"])
    return None