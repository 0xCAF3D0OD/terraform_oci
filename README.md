# SETUP Terraform + Oracle Cloud Infrastructure

## Philosophie et Architecture de Sécurité

### L'Objectif : Le Principe du "Moindre Privilège"

Le but de cette configuration est de passer d'un système où tu fais tout avec un compte "Dieu" (Admin) à un système professionnel sécurisé où chaque personne n'a que les accès nécessaires à son travail.

**Problème initial :**
- Tu utilisais ton compte Admin pour tout
- **Risque :** Une erreur de frappe ou une clé volée = toute ta Tenancy (compte Oracle) compromise

**Solution mise en place : Gouvernance Cloud**

| Bénéfice | Explication |
|----------|-------------|
| **Isolation des risques** | Si l'utilisateur KDI fait une erreur, il ne peut pas supprimer tes ressources d'Administrateur |
| **Droit à l'erreur** | Le compartiment Dev est un "bac à sable" pour tester sans polluer le compte principal |
| **Professionnalisme** | Structure identique aux grandes entreprises (Netflix, Uber) : Utilisateur → Groupe → Policy → Compartiment |

---

### Ce que nous avons construit (Le "Quoi")

| Objet | Emplacement dans la console | Son rôle actuel |
|-------|----------------------------|-----------------|
| **KDI (User)** | Identity > Domains > Users | Ton identité de travail |
| **DevOps (Group)** | Identity > Domains > Groups | Le "porte-clés" (KDI est dedans) |
| **devops-policy** | Identity > Policies | L'autorisation qui nomme le groupe DevOps |
| **compartiment_Dev** | Identity > Compartments | La zone où le groupe a le droit d'agir |

---

### La Chaîne de Confiance (4 maillons)
```
1. Utilisateur (kdi@dev.com)
   ↓ Compte vide, sans aucun droit par défaut
   
2. Groupe (DevOps)
   ↓ Un "contenant" qui porte les droits (scalable : facile d'ajouter 10 nouveaux employés)
   
3. Policy (devops-policy)
   ↓ Le contrat juridique : "Le groupe DevOps a le droit de gérer les serveurs, mais rien d'autre"
   
4. Profil CLI ([KDI])
   ↓ Identité numérique (clés .pem) pour prouver à Oracle qui tu es
```

---

### Les 3 Piliers de la Sécurité

#### La Cloison : Le Compartiment (compartiment_Dev)

**Concept :** On arrête de tout mettre dans la "pièce principale" (Root)

- **Action :** Création d'un espace nommé `compartiment_Dev`
- **Métaphore :** Une pièce sécurisée dans ta maison dont tu as donné les clés à quelqu'un d'autre
- **Bénéfice :** Isolation complète des ressources de test/dev

#### Le Verrou : La Policy (devops-scoped-policy)

**Concept :** Le document juridique qui définit les droits

- **Action :** Statement ultra-précis
```
  Allow group DevOps to manage instance-family in compartment compartiment_Dev
```
- **Mot-clé magique :** `in compartment` = la limite de sécurité
- **Résultat :** En dehors de ce compartiment, le groupe DevOps n'existe pas pour Oracle

#### Le Garde-fou : Le Profil [KDI]

**Concept :** Configuration du terminal pour être prudent par défaut

- **Action :** Identité de KDI (droits limités) en tant que profil par défaut
- **Protection :** Pour une action "dangereuse", tu dois consciemment ajouter `--profile ADMIN`
- **Bénéfice :** Protection contre toi-même (erreurs de manipulation)

---

### Comment nous l'avons fait (Le "Comment")

#### 1. Sécurisation de l'accès

Au lieu d'un simple mot de passe, nous utilisons une **paire de clés API (RSA)** :
```
Clé privée (.pem)  →  Reste sur ton Mac (jamais partagée)
       ↓
Signature numérique
       ↓
Clé publique  →  Donnée à Oracle (peut être publique)
       ↓
Oracle vérifie la signature
```

**Analogie :** C'est comme un badge magnétique. Oracle reconnaît la signature de ta clé.

#### 2. Organisation des droits

**Liaison User → Groupe :**
```bash
oci iam group add-user --user-id <KDI_OCID> --group-id <DEVOPS_GROUP_OCID>
```

**Liaison Groupe → Ressources :**
```
Allow group DevOps to manage instance-family in compartment compartiment_Dev
```

---

### Le Résultat Final : Deux "Casquettes"

Tu as maintenant deux identités distinctes sur ton ordinateur :

| Profil | Casquette | Rôle | Utilisation |
|--------|-----------|------|-------------|
| **[DEFAULT]** (ou **[ADMIN]**) | 👑 Admin | Propriétaire : créer/supprimer des utilisateurs, payer les factures | Actions rares et sensibles |
| **[KDI]** | 👷 DevOps | Technicien : créer des serveurs, gérer le réseau dans compartiment_Dev | Travail quotidien |

**Commandes au quotidien :**
```bash
# Travail normal (utilise automatiquement [KDI])
terraform plan

# Action administrative (doit être explicite)
oci iam user create --name "nouveau-dev" --profile ADMIN
```

---

### État Final de ton Infrastructure

| Élément | État | Rôle |
|---------|------|------|
| **Utilisateur Admin** | Caché derrière `--profile ADMIN` | Le propriétaire, ne touche à rien au quotidien |
| **Utilisateur KDI** | Profil par défaut | Le technicien qui travaille dans son compartiment |
| **Compartiment Dev** | Actif | Zone de test isolée et sécurisée |
| **Policy** | Restrictive | Lie KDI à son compartiment uniquement |

---

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
user=<USER_OCID>
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx
tenancy=<TENANCY_OCID>
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

## Phase 2 : Organisation des ressources Oracle Cloud

### 4. Création du compartiment "compartiment_Dev"
- But : Organiser les ressources par environnement
- Commande : `oci iam compartment create --name "compartiment_Dev" --description "Compartiment de développement" --compartment-id <TENANCY_OCID>`
- OCID obtenu : `<COMPARTMENT_OCID>`

### 5. Création de l'utilisateur DevOps "kdi@dev.com"
- Console Oracle Cloud → Identity → Users → Create User
- Génération de ses clés API (via la console)
- Configuration du profil [KDI] dans `~/.oci/config`

Exemple profil KDI :
```
[KDI]
user=<USER_OCID>
fingerprint=dc:62:87:d0:20:f6:4f:20
tenancy=<TENANCY_OCID>
region=us-ashburn-1
key_file=path/to/.oci/pem_file
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
  --user-id ocid1.user.oc1..xxxxxxxxxxxxxx \
  --group-id <DEVOPS_GROUP_OCID> \
  --profile DEFAULT
```

### 8. Compte ADMIN crée les policies IAM
```bash
oci iam policy create \
  --compartment-id <COMPARTMENT_OCID> \
  --name "devops-compartment-dev-policy" \
  --description "Permissions pour le groupe DevOps" \
  --statements '[
    "Allow group DevOps to manage virtual-network-family in compartment id <COMPARTMENT_OCID>",
    "Allow group DevOps to manage instance-family in compartment id <COMPARTMENT_OCID>"
  ]' \
  --profile DEFAULT
```

---

### For the Terraform configuration see in the [terraform](./terraform/README.terraform.md)

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

---

## Ressources et documentation

- Oracle Cloud Documentation : https://docs.oracle.com/en-us/iaas/
- Terraform OCI Provider : https://registry.terraform.io/providers/oracle/oci/latest/docs
- OCI CLI Reference : https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/
- OCI Free Tier : https://www.oracle.com/cloud/free/
