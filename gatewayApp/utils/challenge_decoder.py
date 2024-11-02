"""
Helper script is used to sign a challenge with a private key.
"""

import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def load_private_key(pem_data):
    """Load a private key from PEM formatted data."""
    return serialization.load_pem_private_key(
        pem_data.encode(),
        password=None
    )

def sign_challenge(private_key, challenge):
    """Sign the challenge using the private key."""
    return private_key.sign(
        challenge,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sign a challenge with a private key.')
    parser.add_argument('-k', '--private_key', required=True, help='Path to the PEM private key file.')
    parser.add_argument('-c', '--challenge', required=True, help='Challenge to be signed.')
    args = parser.parse_args()

    with open(args.private_key, 'r', encoding='utf-8') as f:
        private_key_pem = f.read()

    private_key = load_private_key(private_key_pem)
    challenge_bytes = bytes.fromhex(args.challenge)
    signed_challenge = sign_challenge(private_key, challenge_bytes)
    print("Signed Challenge (hex):", signed_challenge.hex())
