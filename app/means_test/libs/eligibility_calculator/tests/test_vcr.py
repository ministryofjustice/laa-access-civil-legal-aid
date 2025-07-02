import functools
import vcr
import os

custom_vcr = vcr.VCR()


def use_vcr_cassette(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        test_dir = os.path.dirname(f.__code__.co_filename)
        cassette_name = test_dir + "/cassettes/" + f.__name__ + ".yml"
        with custom_vcr.use_cassette(cassette_name):
            return f(*args, **kwargs)

    return wrapper
