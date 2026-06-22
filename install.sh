#!/bin/bash
# Script de instalação do KLayout Lithography Toolbox

KLAYOUT_HOME="$HOME/.klayout"
TARGET_DIR="$KLAYOUT_HOME/salt/klayout-lithography-toolbox"

echo "Instalando Lithography Toolbox para KLayout..."

# Cria o diretório de destino se não existir
mkdir -p "$TARGET_DIR"

# Copia os arquivos necessários
cp -r grain.xml pymacros python "$TARGET_DIR/"

echo "Instalação concluída com sucesso no diretório: $TARGET_DIR"
echo "Por favor, reinicie o KLayout para carregar a biblioteca."
