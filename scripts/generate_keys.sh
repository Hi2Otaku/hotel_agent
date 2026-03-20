#!/bin/bash
set -e

KEYS_DIR="$(dirname "$0")/../keys"
mkdir -p "$KEYS_DIR"

echo "Generating RSA 2048-bit key pair for JWT..."

# Generate private key
openssl genrsa -out "$KEYS_DIR/jwt_private_key" 2048

# Extract public key
openssl rsa -in "$KEYS_DIR/jwt_private_key" -pubout -out "$KEYS_DIR/jwt_public_key"

# Set permissions
chmod 600 "$KEYS_DIR/jwt_private_key"
chmod 644 "$KEYS_DIR/jwt_public_key"

echo "JWT key pair generated successfully in $KEYS_DIR/"
echo "  Private key: $KEYS_DIR/jwt_private_key"
echo "  Public key:  $KEYS_DIR/jwt_public_key"
