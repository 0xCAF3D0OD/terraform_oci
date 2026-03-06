from InquirerPy.utils import get_style

# Codes ANSI
GREEN = "\033[1;32m"  # Bold Green (valeurs)
YELLOW = "\033[1;33m"  # Bold Yellow (labels)
RED = "\033[1;31m"  # Bold Yellow (labels)
RESET = "\033[0m"  # Reset

STYLE = get_style({
        "questionmark": "#e5c07b",
        "message": "#e5c07b bold",
        "pointer": "#61afef bold",
        "answermark": "#98c379",
        "answer": "#98c379 bold",
    },
    style_override=False) # style_override=False permet de garder les couleurs de base pour le reste

# oci_config: {
#   'log_requests': False,
#   'additional_user_agent': '',
#   'pass_phrase': None,
#   'user': 'ocid1.user.oc1..aaaaa...',
#   'fingerprint': '2a:dd:87:...',
#   'tenancy': 'ocid1.tenancy.oc1..aaaa...',
#   'region': 'us-ashburn-1',
#   'key_file': '~/.oci/vrevol_keys/oci_api_key.pem'
# }
config = {
    "oci_config": {},
    "username": "",
    "tenancy_ocid": None,
    "compartment_name": "",
    "parent_compartment_id": None,
    "parent_compartment_name": ""
}
