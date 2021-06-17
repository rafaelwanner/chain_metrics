from ecdsa import SigningKey, VerifyingKey, SECP256k1



def uncompressPublicKey(compressed_pk):
    """
    Constructs the uncompressed representation of a SECP256k1 ECDSA public key form a given compressed key.
    The code is port from https://stackoverflow.com/a/43654055/5413535 with a couple of bug fixed.
    :param compressed_pk: The compressed SECP256k1 key to be decompressed.
    :type compressed_pk: hex
    :return: The uncompressed SECP256k1 ECDSA key.
    :rtype: hex
    """

    # Get p from the curve
    p = SECP256k1.curve.p()

    # Get x and the prefix
    x_hex = compressed_pk[2:66]
    x = int(x_hex, 16)
    prefix = compressed_pk[0:2]

    # Compute y
    y_square = (pow(x, 3, p) + 7) % p
    y_square_square_root = pow(y_square, int((p + 1) / 4), p)

    # Chose the proper y depending on the prefix and whether the computed square root is odd or even
    if prefix == "02" and y_square_square_root & 1 or prefix == "03" and not y_square_square_root & 1:
        y = (-y_square_square_root) % p
    else:
        y = y_square_square_root

    # Construct the uncompressed pk
    uncompressed_pk = "04" + x_hex.decode("utf-8") + format(y, '064x')

    return bytearray(uncompressed_pk, 'utf-8')