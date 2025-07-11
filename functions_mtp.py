import random
from generator import var_or_const

VOID_FUNCS = ["set_flow_id"]
INT_FUNCS = ["len", "rand", "nanoseconds"]
FLOW_ID_FUNCS = ["get_flow_id", "id"]
CHECKSUM_FUNCS = ["CRC16_t"]
DATA_FUNCS = ["unseg_data", "seg_data"]
INSTR_FUNCS = ["pkt_gen_instr", "timer_start_instr", "timer_cancel_instr", "timer_restart_instr",
               "new_ctx_instr", "new_ordered_data", "add_data_set", "flush_and_notify", "notify_instr"]

def void_func_call(CURR_EP_EVENT_TYPE, LIST_OF_VARS):
    """
    Generates a random function call that returns void.
    """
    func_id = VOID_FUNCS[0]
    args = []
    args.append(var_or_const(CURR_EP_EVENT_TYPE, LIST_OF_VARS)[0])

    if(None in args):
        return "", "NO_ARG_FLAG"
    return func_id + "(" + ", ".join(args) + ")"

def int_func_call(LIST_OF_VARS):
    """
    Generates a random function call that returns an int.
    """
    func_id = random.choice(INT_FUNCS)
    args = []
    if(func_id == "len"):
        args.append(var_or_const("data_t", LIST_OF_VARS)[0])
    elif(func_id == "nanoseconds"):
        args.append(var_or_const("int", LIST_OF_VARS)[0])

    if(None in args):
        return "", "NO_ARG_FLAG"
    return func_id + "(" + ", ".join(args) + ")"

def flow_id_func_call(LIST_OF_VARS):
    """
    Generates a random function call that returns a flow ID.
    """
    func_id = random.choice(FLOW_ID_FUNCS)
    args = []
    if(func_id == "get_flow_id"):
        args.append(var_or_const("event", LIST_OF_VARS)[0])
    elif(func_id == "id"):
        for _ in range(random.randint(1, 4)):
            args.append(var_or_const("int", LIST_OF_VARS)[0])

    if(None in args):
        return "", "NO_ARG_FLAG"
    return func_id + "(" + ", ".join(args) + ")"

def checksum_func_call(LIST_OF_VARS):
    """
    Generates a random function call that returns a checksum.
    """
    func_id = CHECKSUM_FUNCS[0]
    return func_id + "()"

def data_func_call(PKT_BP_ID, DICT_OF_STRUCTS, LIST_OF_VARS):
    """
    Generates a random function call that returns data.
    """
    func_id = random.choice(DATA_FUNCS)
    args = []
    if(func_id == "unseg_data"):
        args.append(var_or_const("addr_t", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        int_fields = []
        for entry in DICT_OF_STRUCTS[PKT_BP_ID]:
            if entry["type"] in ["int", "int8", "int16", "int32", "int64"]:
                int_fields.append(entry["name"])
        if(int_fields == []):
            return "ERROR IN DATA FUNC CALL"
        args.append(PKT_BP_ID + "::" + random.choice(int_fields))
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])

        if(None in args):
            return "", "NO_ARG_FLAG"
        return func_id + "(" + ", ".join(args[:2]) + ", [" + ", ".join(args[2:])  + "])"
    
    elif(func_id == "seg_data"):
        args.append(var_or_const("addr_t", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])

        if(None in args):
            return "", "NO_ARG_FLAG"
        return func_id + "(" + ", ".join(args) + ")"
    
    return "ERROR IN DATA FUNC CALL"

def instr_func_call(PKT_BP_ID, CURR_EP_EVENT_TYPE, CONTEXT_NAME, LIST_OF_VARS):
    """
    Generates a random function call that returns an instruction.
    """
    func_id = random.choice(INSTR_FUNCS)
    args = []
    if(func_id == "pkt_gen_instr"):
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const(PKT_BP_ID, LIST_OF_VARS)[0])
    elif(func_id == "timer_start_instr"):
        args.append(var_or_const("timer_t", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const(CURR_EP_EVENT_TYPE, LIST_OF_VARS)[0])
    elif(func_id == "timer_cancel_instr"):
        args.append(var_or_const("timer_t", LIST_OF_VARS)[0])
        None
    elif(func_id == "timer_restart_instr"):
        args.append(var_or_const("timer_t", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const(CURR_EP_EVENT_TYPE, LIST_OF_VARS)[0])
    elif(func_id == "new_ctx_instr"):
        args.append(var_or_const(CONTEXT_NAME, LIST_OF_VARS)[0])
        # TODO: each argument must be "context field = value". I need to do this in a loop
    elif(func_id == "new_ordered_data"):
        if(random.randint(0, 1)):
            args.append(var_or_const("int", LIST_OF_VARS)[0])
            args.append(var_or_const("flow_id", LIST_OF_VARS)[0])
            args.append(var_or_const("addr_t", LIST_OF_VARS)[0])
        else:
            args.append(var_or_const("int", LIST_OF_VARS)[0])
            args.append(var_or_const("flow_id", LIST_OF_VARS)[0])
    elif(func_id == "add_data_set"):
        args.append(var_or_const("addr_t", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const("flow_id", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
    elif(func_id == "flush_and_notify"):
        args.append(var_or_const("flow_id", LIST_OF_VARS)[0])
        args.append(var_or_const("int", LIST_OF_VARS)[0])
        args.append(var_or_const("addr_t", LIST_OF_VARS)[0])
    
    if(None in args):
        return "", "NO_ARG_FLAG"
    return func_id + "(" + ", ".join(args) + ")"

def function_call(return_type, pkt_bp_id, dict_of_structs, curr_ep_event_type, context_name, list_of_vars):
    """
    Generates a random function call.
    """
    func_stmt = ""
    if return_type == "void":
        func_stmt = void_func_call(curr_ep_event_type, list_of_vars)
    elif return_type == "int":
        func_stmt = int_func_call(list_of_vars)
    elif return_type == "flow_id":
        func_stmt = flow_id_func_call(list_of_vars)
    elif return_type == "checksum16_t":
        func_stmt = checksum_func_call(list_of_vars)
    elif return_type == "data_t":
        func_stmt = data_func_call(pkt_bp_id, dict_of_structs, list_of_vars)
    elif return_type == "instr_t":
        func_stmt = instr_func_call(pkt_bp_id, curr_ep_event_type, context_name, list_of_vars)
    if(type(func_stmt) is tuple):
        return func_stmt[0], func_stmt[1]
    return func_stmt, return_type