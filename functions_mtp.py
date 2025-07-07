import random
import rstr
from generator import var_or_const

def function_call():
    """
    Generates a random function call.
    """
    func_name = rstr.xeger(r'[a-zA-Z_][a-zA-Z0-9_]{0,10}')
    args = []
    #for _ in range(random.randint(1, 3)):
    #    args.append(var_or_const()[0])
    return func_name + "(" + ")", "int"