# ===== SECTION 1 : Configuration Terraform =====
terraform {
  required_providers {
    oci = {
      source = "oracle/oci" # Où télécharger le plugin Oracle
      version = "~> 5.0" # Version 5.x minimum
    }
  }
  required_version = ">= 1.0.0"
}

# ===== SECTION 2 : Configuration du provider =====
provider "oci" {
  # Utilise automatiquement ~/.oci/config [DEFAULT]
  region = var.oci_region
  auth                = "SecurityToken"
  config_file_profile = var.user
}

resource "oci_core_vcn" "internal" {
  dns_label      = "internal"
  cidr_block     = "172.16.0.0/20"
  compartment_id = var.compartment_ocid
  display_name   = "My internal VCN"
}

# ===== SECTION 3 : Récupère des données d'Oracle =====
# "data" = je veux juste LIRE des infos, pas créer de ressource
# "oci_identity_availability_domains" = le type de données
# "ads" = le nom que je donne à cette requête
# data "oci_identity_availability_domain" "ads" {
#   # compartment_id = dans quel compartment chercher (ici ta tenancy)
#   compartment_id = var.tenancy_compartment_ocid
# }
