import rsa
import os



# получение побличного криптоключа
def load_public_key():
    # Read the public_key
    with open(os.path.dirname(os.path.realpath(__file__)) + '/public_key.txt', "rb") as public_file:
        public_key = rsa.PublicKey.load_pkcs1(public_file.read())
    return public_key


# получение приватного криптоключа
def load_private_key():
    # Read the private_key
    with open(os.path.dirname(os.path.realpath(__file__)) + '/private_key.txt', "rb") as private_file:
        private_key = rsa.PrivateKey.load_pkcs1(private_file.read())
    return private_key