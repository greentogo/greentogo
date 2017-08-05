from hashids import Hashids

_hashids_ = Hashids(salt="greentogo")


def encode_nums(*args):
    return _hashids_.encode(*args)


def decode_id(id):
    return _hashids_.decode(id)
