import oci

def get_compartment_list(
        identity_client: oci.identity.IdentityClient,
        current_id: str,
        parent_name: str,
        list_compartments: dict[str, dict[str, str]]
) -> dict:
    try:
        # Appel API
        list_compartments_response = identity_client.list_compartments(
            compartment_id=current_id,
            sort_by="NAME",
            sort_order="ASC",
            lifecycle_state="ACTIVE"
        )

        for compartment in list_compartments_response.data:
            # On crée un label unique pour éviter d'écraser des doublons (Nom + Parent)
            display_label = f"{compartment.name} (parent: {parent_name})"
            list_compartments[display_label] = {
                "cmp_name": compartment.name,
                "cmp_parent": parent_name,
                "cmp_ocid": compartment.id,
            }
            get_compartment_list(identity_client, compartment.id, compartment.name, list_compartments)

        return list_compartments

    except oci.exceptions.ServiceError as e:
        # Erreur côté OCI (ex: 403 Forbidden si tu n'as pas accès à un sous-compartiment)
        print(f"⚠️  Skipping sub-compartments of {parent_name}: {e.message}")
        return list_compartments
    except Exception as e:
        # Erreur critique (ex: Coupure réseau)
        print(f"❌ Critical error fetching compartments: {e}")
        return list_compartments

def get_groups_list(groups_list: list[dict[str, str]]) -> dict:
    try:
        structured_groups_dict= {}
        for group in groups_list:
            display_label = f"{group.display_name}-{group.id}"

            structured_groups_dict[display_label] = {
                "tenancy_id": group.tenancy_ocid,
                "dmn_id": group.domain_ocid,
                "gp_cmp_id": group.compartment_ocid,
                "gp_ocid": group.id
            }

        return structured_groups_dict

    except oci.exceptions.ServiceError as e:
        # Erreur côté OCI (ex: 403 Forbidden si tu n'as pas accès à un sous-compartiment)
        print(f"⚠️  Service error on {display_label}: {e.message}")
        return {}
    except Exception as e:
        # Erreur critique (ex: Coupure réseau)
        print(f"❌ Critical error fetching compartments: {e}")
        return {}