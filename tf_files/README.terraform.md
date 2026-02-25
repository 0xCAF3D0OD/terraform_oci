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
user             = "X"
compartment_ocid = "<COMPARTMENT_OCID>"
```

### 13. Initialisation Terraform
```bash
cd tf_files-oci
tf_files init
```

---

## Phase 5 : Création des ressources

### 14. Création du VCN via Terraform
Maintenant X (via son appartenance au groupe DevOps) a les permissions pour créer des ressources.

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
tf_files plan    # Prévisualisation
tf_files apply   # Création des ressources
```

---

## Schéma récapitulatif

```bash
tf_files init       # Initialiser le projet
tf_files validate   # Valider la syntaxe
tf_files plan       # Prévisualiser les changements
tf_files apply      # Appliquer les changements
tf_files destroy    # Détruire les ressources
```

---

## Commandes Utiles

### Terraform
```bash
# Initialiser le projet
tf_files init

# Valider la syntaxe
tf_files validate

# Formater le code
tf_files fmt

# Prévisualiser les changements
tf_files plan

# Appliquer les changements
tf_files apply

# Appliquer sans confirmation interactive
tf_files apply -auto-approve

# Détruire toutes les ressources
tf_files destroy

# Afficher l'état actuel
tf_files show

# Lister les ressources gérées
tf_files state list

# Rafraîchir l'état sans modifications
tf_files refresh
```

### Debugging
```bash
# CLI OCI avec debug
oci network vcn list --compartment-id <OCID> --debug --profile X

# Terraform avec logs détaillés
export TF_LOG=DEBUG
tf_files plan

# Désactiver les logs
unset TF_LOG

# Vérifier les fingerprints des clés
openssl rsa -pubout -outform DER -in ~/.oci/X_keys/oci_api_key.pem | openssl md5 -c
```

---

## Ressources et Documention

### Terraform
- **Terraform OCI Provider :** https://registry.terraform.io/providers/oracle/oci/latest/docs
- **Terraform Registry (exemples) :** https://registry.terraform.io/providers/oracle/oci/latest
- **Terraform Best Practices :** https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html

### Tutoriels et exemples
- **OCI Tutorials :** https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm
- **Terraform Examples (GitHub) :** https://github.com/oracle/terraform-provider-oci/tree/master/examples

---

## Troubleshooting : Erreurs Courantes

### Erreur : Terraform "auth = SecurityToken"

**Symptôme :**
```
Error: Service error: NotAuthenticated
```

**Cause :** Utilisation de SecurityToken avec une clé API

**Solution :** Supprimer la ligne `auth = "SecurityToken"` du provider
```hcl
provider "oci" {
  region              = var.oci_region
  config_file_profile = var.user
  # SUPPRIMER: auth = "SecurityToken"
}
```

---

## Checklist de Sécurité

### Avant de commencer

- [ ] Activer MFA (Multi-Factor Authentication) sur le compte Admin
- [ ] Créer des clés API séparées pour chaque utilisateur
- [ ] Ne jamais partager les clés privées (.pem)
- [ ] Stocker les clés privées avec permissions restrictives (`chmod 600`)

### Configuration des droits

- [ ] Principe du moindre privilège : donner uniquement les droits nécessaires
- [ ] Utiliser des groupes plutôt que des permissions directes sur utilisateurs
- [ ] Limiter les policies aux compartiments spécifiques (pas `in tenancy`)
- [ ] Documenter chaque policy créée

### Gestion du code Terraform

- [ ] Ne jamais commiter `terraform.tfvars` avec des secrets
- [ ] Utiliser un `.gitignore` approprié
- [ ] Versionner le code dans Git
- [ ] Utiliser Terraform State en remote (S3, OCI Object Storage)
- [ ] Activer le chiffrement du state file

### Monitoring et audit

- [ ] Activer Cloud Guard (détection de menaces)
- [ ] Configurer des alertes de coûts
- [ ] Réviser régulièrement les permissions IAM
- [ ] Utiliser des tags pour tracer les ressources
