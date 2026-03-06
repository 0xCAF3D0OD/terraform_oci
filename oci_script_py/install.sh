#!/bin/bash
# install.sh

# Crée le venv
python3 -m pip install --upgrade pip && python3 -m venv ~/.venv

# Installe les requirements
~/.venv/bin/pip install -r requirements.txt

# Configure le shebang
sed -i '1s|^|#!/'$HOME'/.venv/bin/python\n|' srcs/oci-resource-ctl

# Rend exécutable
chmod +x srcs/oci-resource-ctl

# (Optionnel) Enlève l'extension .py
# mv oci-resource-ctl.py oci-resource-ctl

echo "✅ Installation terminée ! Lance avec oci-resource-ctl"
