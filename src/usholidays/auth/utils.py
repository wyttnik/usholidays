from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)


unencrypted_pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
    # encryption_algorithm=serialization.BestAvailableEncryption(secret_key),
)

pem_public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

with open("creds/rsa.pem", "w") as private_key_file:
    private_key_file.write(unencrypted_pem_private_key.decode())

with open("creds/rsa.pub", "w") as public_key_file:
    public_key_file.write(pem_public_key.decode())
