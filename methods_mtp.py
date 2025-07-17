import random


def add_method_call(LIST_OF_VARS):
    """
    Generates a random method call that adds a new element to a list.
    """
    from generator import var_or_const
    var = var_or_const("list", LIST_OF_VARS)
    if(var[1] == "NO_ARG_FLAG"):
        return None
    type = var[1].split("<")[1].split(">")[0]
    arg = var_or_const(type, LIST_OF_VARS)[0]
    return var[0] + ".add(" + arg + ")"

def set_method_call(LIST_OF_VARS):
    """
    Generates a random method call that sets a new interval in a sliding window.
    """
    from generator import var_or_const
    var = var_or_const("sliding_wnd", LIST_OF_VARS)
    if(var[1] == "NO_ARG_FLAG"):
        return None
    arg1 = var_or_const("int", LIST_OF_VARS)[0]
    arg2 = var_or_const("int", LIST_OF_VARS)[0]
    return var[0] + ".set(" + arg1 + ", " + arg2 + ")"

def unset_method_call(LIST_OF_VARS):
    """
    Generates a random method call that retrieves the first unset field of a sliding window.
    """
    from generator import var_or_const
    var = var_or_const("sliding_wnd", LIST_OF_VARS)
    if(var[1] == "NO_ARG_FLAG"):
        return None
    return var[0] + ".first_unset()"

def method_call(list_of_vars):
    """
    Generates a random method call.
    """
    for i in range(random.randint(1, 10)):
        rnd_num = random.randint(0, 2)
        #if(rnd_num == 3):
        #    return extract_method_call()
        if(rnd_num == 2):
            return add_method_call(list_of_vars)
        elif(rnd_num == 1):
            return set_method_call(list_of_vars)
        else:
            return unset_method_call(list_of_vars)


    return None