#!/usr/bin/env bash
# ==============================================================================
# Palmer Penguins — Linux desktop shortcut installer
# Author: Jean Carlos Rojas Herrera (RojasJeanDL)
#
# Generates a .desktop launcher pointing at THIS clone of the repository.
#
# The shortcut is generated rather than committed on purpose: a .desktop entry
# needs an absolute Exec/Path, so a committed one would carry the original
# author's directory layout and fail on every other machine.
# ==============================================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
DESKTOP_FILE="${APPLICATIONS_DIR}/palmer-penguins-dashboard.desktop"

if [ ! -f "${PROJECT_DIR}/run_dashboard.sh" ]; then
    echo "[ERROR] run_dashboard.sh not found in ${PROJECT_DIR}" >&2
    exit 1
fi

chmod +x "${PROJECT_DIR}/run_dashboard.sh"
mkdir -p "${APPLICATIONS_DIR}"

cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Palmer Penguins AI & Analytics Dashboard
Name[es]=Palmer Penguins Dashboard de Análisis e IA
Comment=Interactive Executive Dashboard for Palmer Penguins (CC0 & Custom Data)
Comment[es]=Dashboard Ejecutivo Interactivo para Palmer Penguins (Datos CC0 y Personalizados)
Exec=${PROJECT_DIR}/run_dashboard.sh
Path=${PROJECT_DIR}
Icon=utilities-terminal
Terminal=true
Categories=Science;DataScience;Education;
EOF

chmod +x "${DESKTOP_FILE}"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${APPLICATIONS_DIR}" >/dev/null 2>&1 || true
fi

echo "[SUCCESS] Shortcut installed: ${DESKTOP_FILE}"
echo "          Target project:     ${PROJECT_DIR}"
echo "          Look for 'Palmer Penguins' in your application menu."
