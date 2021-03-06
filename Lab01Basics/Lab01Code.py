#####################################################
# GA17 Privacy Enhancing Technologies -- Lab 01
#
# Basics of Petlib, encryption, signatures and
# an end-to-end encryption system.
#
# Run the tests through:
# $ py.test-2.7 -v Lab01Tests.py 

###########################
# Group Members: TODO
###########################


#####################################################
# TASK 1 -- Ensure petlib is installed on the System
#           and also pytest. Ensure the Lab Code can 
#           be imported.

import petlib

#####################################################
# TASK 2 -- Symmetric encryption using AES-GCM 
#           (Galois Counter Mode)
#
# Implement a encryption and decryption function
# that simply performs AES_GCM symmetric encryption
# and decryption using the functions in petlib.cipher.

from os import urandom
from petlib.cipher import Cipher

def encrypt_message(K, message):
    """ Encrypt a message under a key K """

    plaintext = message.encode("utf8")
    
    ## YOUR CODE HERE
    block_size = 16
    aes = Cipher("aes-128-gcm")
    iv = urandom(block_size)

    ciphertext, tag = aes.quick_gcm_enc(K, iv, plaintext)

    return (iv, ciphertext, tag)

def decrypt_message(K, iv, ciphertext, tag):
    """ Decrypt a cipher text under a key K 

        In case the decryption fails, throw an exception.
    """
    ## YOUR CODE HERE
    aes = Cipher("aes-128-gcm")
    plain = aes.quick_gcm_dec(K, iv, ciphertext, tag)

    return plain.encode("utf8")

#####################################################
# TASK 3 -- Understand Elliptic Curve Arithmetic
#           - Test if a point is on a curve.
#           - Implement Point addition.
#           - Implement Point doubling.
#           - Implement Scalar multiplication (double & add).
#           - Implement Scalar multiplication (Montgomery ladder).
#
# MUST NOT USE ANY OF THE petlib.ec FUNCIONS. Only petlib.bn!

from petlib.bn import Bn


def is_point_on_curve(a, b, p, x, y):
    """
    Check that a point (x, y) is on the curve defined by a,b and prime p.
    Reminder: an Elliptic Curve on a prime field p is defined as:

              y^2 = x^3 + ax + b (mod p)
                  (Weierstrass form)

    Return True if point (x,y) is on curve, otherwise False.
    By convention a (None, None) point represents "infinity".
    """
    assert isinstance(a, Bn)
    assert isinstance(b, Bn)
    assert isinstance(p, Bn) and p > 0
    assert (isinstance(x, Bn) and isinstance(y, Bn)) \
           or (x is None and y is None)

    if x is None and y is None:
        return True

    lhs = (y * y) % p
    rhs = (x**3 + a*x + b) % p
    if (rhs == lhs):
        return True
    else:
        return False

def point_add(a, b, p, x0, y0, x1, y1):
    """Define the "addition" operation for 2 EC Points.

    Reminder: (xr, yr) = (xq, yq) + (xp, yp)
    is defined as:
        lam = (yq - yp) * (xq - xp)^-1 (mod p)
        xr  = lam^2 - xp - xq (mod p)
        yr  = lam * (xp - xr) - yp (mod p)

    Return the point resulting from the addition. Raises an Exception if the points are equal.
    """

    # ADD YOUR CODE BELOW
    if not is_point_on_curve(a, b, p, x0, y0) or not is_point_on_curve(a, b, p, x1, y1):
        # Check if point any of the points are not on the curve
        raise Exception("Both points must be on the curve")
    elif (x0 is None and y0 is None):
        # Neutral elements are those when (x0, y0) + (None, None) == (x0, y0) and vice versa
        return x1, y1
    elif (x1 is None and y1 is None):
        return x0, y0
    elif ((x0, y0) == (x1, y1)):
        # Check if the points are equal ONLY IF they are not None. As this causes and error when
        # using == for None
        raise Exception("EC Points must not be equal") 
    elif ((x0 % p == x1 % p) or (y0 % p == y1 % p)):
        return None, None
    else:
        if x0 is None or x1 is None or y0 is None or y1 is None:
            # Use normal operations if input values have None 
            lam = ((y1 - y0) * ((x1 - x0).mod_inverse(p))) % p
            xr = (pow(lam, 2) - x1 - x0) % p
            yr = (lam * ((x0 - xr)) - y0) % p
        else:
            # If none of the coordaintes are None we can use Bn Operations
            lam = (y1.int_sub(y0)).int_mul((x1-x0).mod_inverse(p)) % p
            xr = (pow(lam, 2).int_sub(x1)).mod_sub(x0, p)
            yr = (lam.int_mul(x0.int_sub(xr))).mod_sub(y0, p)
        return xr, yr
    

def point_double(a, b, p, x, y):
    """Define "doubling" an EC point.
     A special case, when a point needs to be added to itself.

     Reminder:
        lam = (3 * xp ^ 2 + a) * (2 * yp) ^ -1 (mod p)
        xr  = lam ^ 2 - 2 * xp
        yr  = lam * (xp - xr) - yp (mod p)

    Returns the point representing the double of the input (x, y).
    """  

    # ADD YOUR CODE BELOW
    if not is_point_on_curve(a, b, p, x, y):
        ## Handle edge case of point not being on curve
        raise Exception("Point must be on curve")
    elif x is None and y is None:
        ## Adding infinity point to itself results in infinity
        return x, y
    else:
        lam = (((3 * pow(x, 2)) + a) * ((2 * y).mod_inverse(p))) % p
        xr = ((pow(lam, 2) - 2 * x)) % p
        yr = ((lam * (x - xr)) - y) % p
        return xr, yr

def point_scalar_multiplication_double_and_add(a, b, p, x, y, scalar):
    """
    Implement Point multiplication with a scalar:
        r * (x, y) = (x, y) + ... + (x, y)    (r times)

    Reminder of Double and Multiply algorithm: r * P
        Q = infinity
        for i = 0 to num_bits(P)-1
            if bit i of r == 1 then
                Q = Q + P
            P = 2 * P
        return Q

    """

    if not is_point_on_curve(a, b, p, x, y):
        raise Exception("Point must be on curve")
    elif x is None and y is None:
        return (None, None)
    else:
        Q = (None, None)
        P = (x, y)
        convert_to_binary_string = str(bin(scalar))[::-1]

        for i in range(scalar.num_bits()):
            if convert_to_binary_string[i] == "1":
                Q = point_add(a, b, p, Q[0], Q[1], P[0], P[1])
            P = point_double(a, b, p, P[0], P[1])
        return Q

def point_scalar_multiplication_montgomerry_ladder(a, b, p, x, y, scalar):
    """
    Implement Point multiplication with a scalar:
        r * (x, y) = (x, y) + ... + (x, y)    (r times)

    Reminder of Double and Multiply algorithm: r * P
        R0 = infinity
        R1 = P
        for i in num_bits(P)-1 to zero:
            if di = 0:
                R1 = R0 + R1
                R0 = 2R0
            else
                R0 = R0 + R1
                R1 = 2 R1
        return R0

    """
    if not is_point_on_curve(a, b, p, x, y):
        raise Exception("Point must be on curve")
    elif x is None and y is None:
        return (None, None)
    else:
        R0 = (None, None)
        R1 = (x, y)
        convert_to_binary_string = str(bin(scalar))[::-1]
        for i in reversed(range(0,scalar.num_bits())):
            if convert_to_binary_string[i] == "0":
                R1 = point_add(a, b, p, R0[0], R0[1], R1[0], R1[1])
                R0 = point_double(a, b, p, R0[0], R0[1])
            else:
                R0 = point_add(a, b, p, R0[0], R0[1], R1[0], R1[1])
                R1 = point_double(a, b, p, R1[0], R1[1])
        return R0


#####################################################
# TASK 4 -- Standard ECDSA signatures
#
#          - Implement a key / param generation 
#          - Implement ECDSA signature using petlib.ecdsa
#          - Implement ECDSA signature verification 
#            using petlib.ecdsa

from hashlib import sha256
from petlib.ec import EcGroup
from petlib.ecdsa import do_ecdsa_sign, do_ecdsa_verify

def ecdsa_key_gen():
    """ Returns an EC group, a random private key for signing 
        and the corresponding public key for verification"""
    G = EcGroup()
    priv_sign = G.order().random()
    pub_verify = priv_sign * G.generator()
    return (G, priv_sign, pub_verify)


def ecdsa_sign(G, priv_sign, message):
    """ Sign the SHA256 digest of the message using ECDSA and return a signature """
    plaintext =  message.encode("utf8")

    ## YOUR CODE HERE
    digest = sha256(plaintext).digest()
    sig = do_ecdsa_sign(G, priv_sign, digest)
    return sig

def ecdsa_verify(G, pub_verify, message, sig):
    """ Verify the ECDSA signature on the message """
    plaintext =  message.encode("utf8")

    ## YOUR CODE HERE
    digest = sha256(plaintext).digest()
    res = do_ecdsa_verify(G, pub_verify, sig, digest)
    return res

#####################################################
# TASK 5 -- Diffie-Hellman Key Exchange and Derivation
#           - use Bob's public key to derive a shared key.
#           - Use Bob's public key to encrypt a message.
#           - Use Bob's private key to decrypt the message.
#
# NOTE: 

def dh_get_key():
    """ Generate a DH key pair """
    G = EcGroup()
    priv_dec = G.order().random()
    pub_enc = priv_dec * G.generator()
    return (G, priv_dec, pub_enc)


def dh_encrypt(pub, message, aliceSig = None):
    """ Assume you know the public key of someone else (Bob), 
    and wish to Encrypt a message for them.
        - Generate a fresh DH key for this message.
        - Derive a fresh shared key.
        - Use the shared key to AES_GCM encrypt the message.
        - Optionally: sign the message with Alice's key.
    """
    G,  priv_a, pub_a = dh_get_key()

    shared_key = sha256((priv_a * pub).export()).digest()[:16] #(pub)^priv_a mod p
    iv, ciphertext, tag = encrypt_message(shared_key, message)

    cipher_elements = (iv, ciphertext, tag, pub_a)

    return cipher_elements


def dh_decrypt(priv, ciphertext, aliceVer = None):
    """ Decrypt a received message encrypted using your public key, 
    of which the private key is provided. Optionally verify 
    the message came from Alice using her verification key."""
    
    ## to decrypt we require iv, ciphertext, tag which can be passed into ciphpertext
    iv, ciphertext, tag, pub_a = ciphertext[0], ciphertext[1], ciphertext[2], ciphertext[3]
    shared_key = sha256((priv * pub_a).export()).digest()[:16] #(pub)^priv_a mod p
    decrypted_message = decrypt_message(shared_key, iv, ciphertext, tag)

    return decrypted_message

## NOTE: populate those (or more) tests
#  ensure they run using the "py.test filename" command.
#  What is your test coverage? Where is it missing cases?
#  $ py.test-2.7 --cov-report html --cov Lab01Code Lab01Code.py 

def test_encrypt():

    message_to_encrypt = "Hello World"
    G, priv_a, pub_b = dh_get_key()

    my_cipher_elements = dh_encrypt(pub_b, message_to_encrypt)

    assert len(my_cipher_elements[0]) == 16
    assert len(my_cipher_elements[1]) == len(message_to_encrypt)
   

def test_decrypt():

    message_to_encrypt = "Hello World"
    G, priv_b, pub_b = dh_get_key()
    my_cipher_elements = dh_encrypt(pub_b, message_to_encrypt)

    decrypted_message = dh_decrypt(priv_b, my_cipher_elements)
    
    assert decrypted_message == "Hello World"
    assert len(decrypted_message) == len(message_to_encrypt)
    

from pytest import raises
def test_fails():

    message_to_encrypt = "Can we make these tests fail? of course we can"

    G, priv_b, pub_b = dh_get_key()

    #  returns (iv, ciphertext, tag, pub_a)
    my_cipher_elements = dh_encrypt(pub_b, message_to_encrypt)
    my_cipher_elements_mutable = [my_cipher_elements[0], my_cipher_elements[1], my_cipher_elements[2], my_cipher_elements[3]]
    
    # Now we test how the decryption can fail based on different inputs

    # bad Key
    with raises(Exception) as exception_info:
        dh_decrypt(11223344, my_cipher_elements_mutable)
    assert "Cipher: decryption failed" in str(exception_info.value)

    # Bad iv
    my_cipher_elements_mutable[0] = my_cipher_elements_mutable[0] + str(1)
    with raises(Exception) as exception_info:
        dh_decrypt(priv_b, my_cipher_elements_mutable)
    assert "Cipher: decryption failed" in str(exception_info.value)

    # Wrong public key from Alice
    my_cipher_elements_mutable[3] = my_cipher_elements_mutable[3].pt_mul(100)
    with raises(Exception) as exception_info:
        dh_decrypt(priv_b, my_cipher_elements_mutable)
    assert "Cipher: decryption failed" in str(exception_info.value)
#####################################################
# TASK 6 -- Time EC scalar multiplication
#             Open Task.
#           
#           - Time your implementations of scalar multiplication
#             (use time.clock() for measurements)for different 
#              scalar sizes)
#           - Print reports on timing dependencies on secrets.
#           - Fix one implementation to not leak information.

def time_scalar_mul():
    pass
