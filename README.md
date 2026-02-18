# SETUP Terraform + Oracle Cloud Infrastructure

## Phase 1 : Configuration de l'authentification Oracle Cloud

### 1. Génération d'une clé de signature d'API (paire publique/privée)
- Commande : `openssl genrsa -out ~/.oci/oci_api_key.pem 2048`
- Génère la clé publique : `openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/apisigningkey.htm

### 2. Installation de la CLI OCI
- Installation : `bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/SDKDocs/cliinstall.htm

### 3. Configuration du compte ADMIN (profil DEFAULT)
- Création du fichier `~/.oci/config` avec les credentials du compte admin
- Upload de la clé publique dans la console Oracle Cloud (User Settings → API Keys)
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/sdkconfig.htm

Exemple de fichier config :
```
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaa7guzlrtcmsqgwwsx72tlllc6rq
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

## Phase 2 : Organisation des ressources Oracle Cloud

### 4. Création du compartiment "compartiment_Dev"
- But : Organiser les ressources par environnement
- Commande : `oci iam compartment create --name "compartiment_Dev" --description "Compartiment de développement" --compartment-id <TENANCY_OCID>`
- OCID obtenu : `ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa`

### 5. Création de l'utilisateur DevOps "kdi@dev.com"
- Console Oracle Cloud → Identity → Users → Create User
- Génération de ses clés API (via la console)
- Configuration du profil [KDI] dans `~/.oci/config`

Exemple profil KDI :
```
[KDI]
user=ocid1.user.oc1..aaaaaaaaxjkpmkqfklpkzq
fingerprint=dc:62:87:d0:20:f6:4f:20
tenancy=ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq
region=us-ashburn-1
key_file=~/.oci/kdi_keys/oci_api_key.pem
```

---

## Phase 3 : Configuration IAM (Identity & Access Management)

### 6. Compte ADMIN crée le groupe "DevOps"
```bash
oci iam group create \
  --name DevOps \
  --description "Groupe pour l'équipe DevOps" \
  --profile DEFAULT
```

### 7. Compte ADMIN ajoute l'utilisateur KDI au groupe DevOps
```bash
oci iam group add-user \
  --user-id ocid1.user.oc1..aaaaaaaaxjkpmkqfklpkzq \
  --group-id <DEVOPS_GROUP_OCID> \
  --profile DEFAULT
```

### 8. Compte ADMIN crée les policies IAM
```bash
oci iam policy create \
  --compartment-id ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq \
  --name "devops-compartment-dev-policy" \
  --description "Permissions pour le groupe DevOps" \
  --statements '[
    "Allow group DevOps to manage virtual-network-family in compartment id ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa",
    "Allow group DevOps to manage instance-family in compartment id ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa"
  ]' \
  --profile DEFAULT
```

---

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
```
Tenancy Oracle Cloud
│
├── Utilisateur ADMIN (kevin.dinocera@protonmail.com)
│   └── Profil [DEFAULT] dans ~/.oci/config
│
├── Utilisateur KDI (kdi@dev.com)
│   └── Profil [KDI] dans ~/.oci/config
│
├── Groupe DevOps
│   └── Contient : KDI
│
├── Policy "devops-compartment-dev-policy"
│   └── "Allow group DevOps to manage virtual-network-family..."
│   └── "Allow group DevOps to manage instance-family..."
│
└── Compartiment "compartiment_Dev"
    └── VCN "internal" (créé par Terraform avec profil KDI)
```

---

## Concepts clés Oracle Cloud

| Concept | Analogie | Équivalent AWS |
|---------|----------|----------------|
| Tenancy | L'immeuble entier | AWS Account |
| Compartiment | Les étages | Organizational Units (OU) |
| Groupe | L'équipe | IAM Group |
| Policy | Le contrat d'accès | IAM Policy |
| VCN | Réseau virtuel | VPC |
| Subnet | Sous-réseau | Subnet |

---

## Commandes utiles

### Vérifier la configuration
```bash
# Tester l'authentification
oci iam user get --user-id <USER_OCID>

# Lister les compartiments
oci iam compartment list --all

# Lister les groupes
oci iam group list --all

# Lister les policies
oci iam policy list --compartment-id <TENANCY_OCID> --all
```

### Terraform
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
- OCI Free Tier : https://www.oracle.com/cloud/free/# SETUP Terraform + Oracle Cloud Infrastructure

## Phase 1 : Configuration de l'authentification Oracle Cloud

### 1. Génération d'une clé de signature d'API (paire publique/privée)
- Commande : `openssl genrsa -out ~/.oci/oci_api_key.pem 2048`
- Génère la clé publique : `openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/apisigningkey.htm

### 2. Installation de la CLI OCI
- Installation : `bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"`
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/SDKDocs/cliinstall.htm

### 3. Configuration du compte ADMIN (profil DEFAULT)
- Création du fichier `~/.oci/config` avec les credentials du compte admin
- Upload de la clé publique dans la console Oracle Cloud (User Settings → API Keys)
- Documentation : https://docs.oracle.com/fr-fr/iaas/Content/API/Concepts/sdkconfig.htm

Exemple de fichier config :
```
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaa7guzlrtcmsqgwwsx72tlllc6rq
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

## Phase 2 : Organisation des ressources Oracle Cloud

### 4. Création du compartiment "compartiment_Dev"
- But : Organiser les ressources par environnement
- Commande : `oci iam compartment create --name "compartiment_Dev" --description "Compartiment de développement" --compartment-id <TENANCY_OCID>`
- OCID obtenu : `ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa`

### 5. Création de l'utilisateur DevOps "kdi@dev.com"
- Console Oracle Cloud → Identity → Users → Create User
- Génération de ses clés API (via la console)
- Configuration du profil [KDI] dans `~/.oci/config`

Exemple profil KDI :
```
[KDI]
user=ocid1.user.oc1..aaaaaaaaxjkpmkqfklpkzq
fingerprint=dc:62:87:d0:20:f6:4f:20
tenancy=ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq
region=us-ashburn-1
key_file=~/.oci/kdi_keys/oci_api_key.pem
```

---

## Phase 3 : Configuration IAM (Identity & Access Management)

### 6. Compte ADMIN crée le groupe "DevOps"
```bash
oci iam group create \
  --name DevOps \
  --description "Groupe pour l'équipe DevOps" \
  --profile DEFAULT
```

### 7. Compte ADMIN ajoute l'utilisateur KDI au groupe DevOps
```bash
oci iam group add-user \
  --user-id ocid1.user.oc1..aaaaaaaaxjkpmkqfklpkzq \
  --group-id <DEVOPS_GROUP_OCID> \
  --profile DEFAULT
```

### 8. Compte ADMIN crée les policies IAM
```bash
oci iam policy create \
  --compartment-id ocid1.tenancy.oc1..aaaaaaaapho2hgmovkuhdws34bwq \
  --name "devops-compartment-dev-policy" \
  --description "Permissions pour le groupe DevOps" \
  --statements '[
    "Allow group DevOps to manage virtual-network-family in compartment id ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa",
    "Allow group DevOps to manage instance-family in compartment id ocid1.compartment.oc1..aaaaaaaa66x3adqtblfqi3g235keznqa"
  ]' \
  --profile DEFAULT
```

---

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
```
Tenancy Oracle Cloud
│
├── Utilisateur ADMIN (kevin.dinocera@protonmail.com)
│   └── Profil [DEFAULT] dans ~/.oci/config
│
├── Utilisateur KDI (kdi@dev.com)
│   └── Profil [KDI] dans ~/.oci/config
│
├── Groupe DevOps
│   └── Contient : KDI
│
├── Policy "devops-compartment-dev-policy"
│   └── "Allow group DevOps to manage virtual-network-family..."
│   └── "Allow group DevOps to manage instance-family..."
│
└── Compartiment "compartiment_Dev"
    └── VCN "internal" (créé par Terraform avec profil KDI)
```

---

## Concepts clés Oracle Cloud

| Concept | Analogie | Équivalent AWS |
|---------|----------|----------------|
| Tenancy | L'immeuble entier | AWS Account |
| Compartiment | Les étages | Organizational Units (OU) |
| Groupe | L'équipe | IAM Group |
| Policy | Le contrat d'accès | IAM Policy |
| VCN | Réseau virtuel | VPC |
| Subnet | Sous-réseau | Subnet |

---

## Commandes utiles

### Vérifier la configuration
```bash
# Tester l'authentification
oci iam user get --user-id <USER_OCID>

# Lister les compartiments
oci iam compartment list --all

# Lister les groupes
oci iam group list --all

# Lister les policies
oci iam policy list --compartment-id <TENANCY_OCID> --all
```

### Terraform
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
