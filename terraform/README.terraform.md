# SETUP Terraform

## Phase 4 : Configuration Terraform

### 9. Structure du projet Terraform
```
terraform-oci/
├── main.tf              # Provider + ressources
├── variables.tf         # Déclarations des variables
├── terraform.tfvars     # Valeurs des variables
└── outputs.tf           # (optionnel) Outputs
```

### 10. Configuration du provider OCI (main.tf)
```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  region              = var.oci_region
  config_file_profile = var.user
}
```

### 11. Fichier variables.tf
```hcl
variable "oci_region" {
  description = "Région OCI"
  type        = string
}

variable "user" {
  description = "Profil utilisateur dans ~/.oci/config"
  type        = string
}

variable "compartment_ocid" {
  description = "OCID du compartiment"
  type        = string
}
```

### 12. Fichier terraform.tfvars
```hcl
oci_region       = "us-ashburn-1"
user             = "KDI"
compartment_ocid = "ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa"
```

### 13. Initialisation Terraform
```bash
cd terraform-oci
terraform init
```

---

## Phase 5 : Création des ressources

### 14. Création du VCN via Terraform
Maintenant KDI (via son appartenance au groupe DevOps) a les permissions pour créer des ressources.

Exemple de ressource VCN dans main.tf :
```hcl
resource "oci_core_vcn" "internal" {
  compartment_id = var.compartment_ocid
  cidr_block     = "172.16.0.0/20"
  display_name   = "My internal VCN"
  dns_label      = "internal"
}
```

Commandes Terraform :
```bash
terraform plan    # Prévisualisation
terraform apply   # Création des ressources
```

---

## Schéma récapitulatif

```bash
terraform init       # Initialiser le projet
terraform validate   # Valider la syntaxe
terraform plan       # Prévisualiser les changements
terraform apply      # Appliquer les changements
terraform destroy    # Détruire les ressources
```

---

## Ressources et documentation

- Oracle Cloud Documentation : https://docs.oracle.com/en-us/iaas/
- Terraform OCI Provider : https://registry.terraform.io/providers/oracle/oci/latest/docs
- OCI CLI Reference : https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/
- OCI Free Tier : https://www.oracle.com/cloud/free/
