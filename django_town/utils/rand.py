import random

ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                       'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                       '0123456789')


def generate_random_from_vschar_set(length=30):
    rand = random.SystemRandom()
    return ''.join(rand.choice(ASCII_CHARACTER_SET) for x in range(length))
