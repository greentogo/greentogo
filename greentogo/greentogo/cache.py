from hashlib import md5


def make_key(key, key_prefix, version):
    return ':'.join([key_prefix, str(version), md5(key.encode("UTF-8")).hexdigest()])
