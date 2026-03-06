# Infrastructure Management Tool

- Warning it's still in developpment

## 1. System Architecture Overview

The script functions as an "assembly line" where each module has a precise role:

```
graph TD
    A[user_managment.py - MAIN] --> B(Validation IAM)
    A --> C{Process Selection}
    
    C -->|2A. New Compartment| D[compartiment.py]
    C -->|3A. New Policy| E[policy.py]
    
    D --> F[inquire_managment.py]
    E --> F
    
    F -->|Recursion| G[(OCI Cloud: Tenancy / Compartments)]
    
    subgraph "Validation & Configuration"
    B
    H[config.py]
    end
```

## 2. How It Works

The system is an interactive assistant that automates administrative tasks on Oracle Cloud (OCI). It is broken down into three phases:

1. **Identification & Rights:** The script identifies the user via their OCI domain, then performs an immediate "check-up" of their permissions to prevent launching an action that will fail due to insufficient rights.

2. **Exploration:** Through recursion in `inquire_managment.py`, the script "scans" your entire company hierarchy to present you with a clear list of available parents.

3. **Standardized Action:** When creating (example: compartment), the script enforces a naming format (`cmp-name-env`) and automatically generates traceability tags (who created what, when, and what is the parent project).

## 3. Getting Started

### Prerequisites

* Python 3.10+ installed.
* OCI CLI configured: A valid `~/.oci/config` file with your API keys.
* `.env` file: Must contain your OCI domains (ex: `EDUCHAT_DOMAIN=https://...`).
* Libraries: `pip install oci InquirerPy python-dotenv`.

### Commands

To launch the tool:

```bash
python3 user_managment.py
```

### Simple Example: Creating a Test Compartment

1. **Launch:** Select `2A. -- new compartment`.
2. **User:** Select your profile (ex: `vincentRevole`).
3. **Target:** Choose the parent from the list: `dk_company (parent: Tenancy)`.
4. **Input:**
   * Name: `cmp-educhat-test`
   * Description: `Temporary test environment`.
5. **Validation:** The script displays a summary. You type `Y`.
   * **Result:** The compartment is created with the tags `project: educhat` and `env: test` automatically extracted from the name.
