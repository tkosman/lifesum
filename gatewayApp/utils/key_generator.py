"""
Helper script which generates a public/private key pair using the RSA algorithm.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_test_key_pair():
    """Generates a test RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key_pem.decode(), public_key_pem.decode()

if __name__ == "__main__":
    private_pem, public_pem = generate_test_key_pair()
    print("Private Key:")
    print(private_pem)

    print("\nPublic Key:")
    print(public_pem)
