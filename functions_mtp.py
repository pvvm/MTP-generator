import random
from generator import var_or_const

VOID_FUNCS = ["set_flow_id"]
INT_FUNCS = ["len", "rand", "nanoseconds"]
FLOW_ID_FUNCS = ["get_flow_id", "id"]
CHECKSUM_FUNCS = ["CRC16_t"]
DATA_FUNCS = ["unseg_data", "seg_data"]
INSTR_FUNCS = ["pkt_gen_instr", "timer_start_instr", "timer_cancel_instr", "timer_restart_instr",
               "new_ctx_instr", "new_ordered_data", "add_data_set", "flush_and_notify", "notify_instr"]

def void_func_call():
    """
    Generates a random function call that returns void.
    """
    func_id = VOID_FUNCS[0]
    args = ""
    for _ in range(2):
        args.append(var_or_const()[0])
    return func_id + "(" + ", ".join(args) + ")", "void"

def function_call(return_type):
    """
    Generates a random function call.
    """
    if return_type == "void":
        void_func_call()
    elif return_type == "int":
        func = random.choice(INT_FUNCS)
        
    args = []
    #for _ in range(random.randint(1, 3)):
    #    args.append(var_or_const()[0])
    return "aiaiai" + "(" + ")", "int"