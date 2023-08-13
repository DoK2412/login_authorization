import rsa
import os



# используется только при старте приложения для создания криптографических кдлючей

# def save_key(public_key, private_key):
#     # Save the public_key
#     with open("public_key.txt", "wb") as public_file:
#         public_file.write(public_key.save_pkcs1())
#
#     # Save the private_key
#     with open("private_key.txt", "wb") as private_file:
#         private_file.write(private_key.save_pkcs1())

# public_key1, private_key1 = rsa.newkeys(1024)



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