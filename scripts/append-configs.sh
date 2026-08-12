#!/usr/bin/env bash
set -e

CONFIG_DIR="waltid/issuer-api2/config"
METADATA_FILE="$CONFIG_DIR/credential-issuer-metadata.conf"
PROFILES_FILE="$CONFIG_DIR/issuer2-profiles.conf"

METADATA_BAK="$CONFIG_DIR/credential-issuer-metadata.conf.bak"
PROFILES_BAK="$CONFIG_DIR/issuer2-profiles.conf.bak"

# Step 1: Create backup if backup does not exist yet
if [ -f "$METADATA_FILE" ] && [ ! -f "$METADATA_BAK" ]; then
    cp "$METADATA_FILE" "$METADATA_BAK"
    echo "[+] Created backup: $METADATA_BAK"
fi

if [ -f "$PROFILES_FILE" ] && [ ! -f "$PROFILES_BAK" ]; then
    cp "$PROFILES_FILE" "$PROFILES_BAK"
    echo "[+] Created backup: $PROFILES_BAK"
fi

# Step 2: Reset config files from backup to clean previous extra appended configs
if [ -f "$METADATA_BAK" ]; then
    cp "$METADATA_BAK" "$METADATA_FILE"
    echo "[+] Reset $METADATA_FILE from backup"
fi

if [ -f "$PROFILES_BAK" ]; then
    cp "$PROFILES_BAK" "$PROFILES_FILE"
    echo "[+] Reset $PROFILES_FILE from backup"
fi

# Step 3: Run the .NET generator to generate and append new entity configs
dotnet run --project Application

echo "[+] Successfully updated and appended configs to waltid/issuer-api2/config/"
