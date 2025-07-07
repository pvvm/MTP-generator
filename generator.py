import random
import rstr
from functions_mtp import *

# TODO: add function/method call
# TODO: add a way to different EPs to be shared between events

STRUCT = 1
EVENT = 2

SCOPE_CNT = 0

INT_TYPE = ["int8", "int16", "int32", "int64"]
FLOAT_TYPE = ["float"]
BOOL_TYPE = ["bool"]
LIST_TYPE = ["list"]

BINARY_OPS = ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]
UNARY_OPS = ["-", "!"]

"""
Each entry of this list is a list representing a scope.
Each inner list contains dictionaries representing variables.
Each dictionary has two keys:
- "name": the name of the variable
- "type": the type of the variable
"""
LIST_OF_VARS = []

# Counter of variables that the current scope has access to.
VAR_CNT = 0

"""
Dictionary that holds the struct-like defined in the code.
The keys are the struct names, and the values are lists of dictionaries
representing the variables in the struct.
Each dictionary has two keys:
- "name": the name of the variable
- "type": the type of the variable
"""
DICT_OF_STRUCTS = {}

"""
List of struct (only actual struct, not struct-like) and packet blueprint
 IDs that are used in the code.
"""
STRUCT_PKT_BP_IDS = []


"""
Dictionary that holds the event processors that process each type of event.
The keys are the event names, and the values are lists of event processor
name that process that event.
"""
DICT_OF_EV_EP = {}

"""
Dictionary that holds the event variable declarations.
The keys are the event types ("APP", "NET", "TIMER"), and the values are dictionaries
that hold the event names and their variable declarations.
The keys of the inner dictionaries are the event names, and the values are lists of dictionaries
representing the variables in the event.
Each dictionary has two keys:
- "name": the name of the variable
- "type": the type of the variable
"""
DICT_OF_EV_DECL = {"APP": {}, "NET": {}, "TIMER": {}}

# Type of the value returned by the current event processor.
CURR_EP_RETURN_TYPE = ""

# Name of the context and scratchpad used in the code.
CONTEXT_NAME = ""
SCRATCH_NAME = ""

def indentation():
    """
    Returns a string with the current indentation level.
    """
    return "\t" * SCOPE_CNT

def get_type():
    """
    Generates a random type declaration.
    """
    types = INT_TYPE + FLOAT_TYPE + BOOL_TYPE + LIST_TYPE
    return random.choice(types)

def var_id():
    """
    Generates a random variable identifier.
    """
    return rstr.xeger(r'[A-Za-z_][A-Za-z0-9_]{0,10}')

def catch_struct_value(struct_id, struct_fields):
    """
    Returns a random field from a struct-like instance.
    """
    random_field = random.choice(struct_fields)
    return struct_id + "." + random_field["name"], random_field["type"]

def catch_var_id(var_type=None):
    index = 0
    if var_type == None:
        while True:
            index = random.randint(0, len(LIST_OF_VARS) - 1)
            if(len(LIST_OF_VARS[index]) > 0):
                break
        random_var = random.choice(LIST_OF_VARS[index])
        struct_id = random_var["type"]
        # Check if the variable is a struct-like variable
        if(struct_id in DICT_OF_STRUCTS):
            return catch_struct_value(struct_id, DICT_OF_STRUCTS[struct_id])
        return random_var["name"], random_var["type"]
    
    list_vars = []
    for entry in LIST_OF_VARS:
        for var in entry:
            if(var["type"] == var_type):
                list_vars.append(var["name"])
    
    if(list_vars == []):
        print("PROBLEM HEREEEEEE")
        return None, var_type
    
    random_var = random.choice(list_vars)
    return random_var, var_type

def var_or_const(var_type=None):
    """
    Returns a variable or a random constant.
    """
    if((random.randint(0, 2) < 2 and len(LIST_OF_VARS) > 0 and VAR_CNT > 0)
       or var_type not in ["int", "float"]):
        return catch_var_id()
    else:
        # Generate a random int
        if(random.randint(0, 1)):
            return rstr.xeger(r'[0-9]{1,10}'), "int"
        # Generate a random float
        else:
            return rstr.xeger(r'[0-9]{1,10}[.][0-9]{1,5}'), "float"

def expression():
    """
    Generates a random expression.
    """
    while(1):
        rnd_num = random.randint(0, 4)
        if(rnd_num == 4):
            # Function call
            return function_call()
        if(rnd_num == 3):
            # Binary operation
            exp_str_1, type_1 = var_or_const()
            exp_str_2, type_2 = expression()
            operation = random.choice(BINARY_OPS)
            if(type_1 not in ["int", "float", "bool"] or type_2 not in ["int", "float", "bool"]):
                continue
            if(operation in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]):
                return exp_str_1 + " " + operation + " " + exp_str_2, "bool"
            if(type_1 == "float" or type_2 == "float"):
                return exp_str_1 + " " + operation + " " + exp_str_2, "float"
            return exp_str_1 + " " + operation + " " + exp_str_2, "int"
        elif(rnd_num == 2):
            # Unary operation
            exp_str, type = expression()
            if(type not in ["int", "float", "bool"]):
                continue
            return random.choice(UNARY_OPS) + exp_str, type
        elif(rnd_num == 1):
            # Nested expression
            exp_str, type = expression()
            return "(" + exp_str + ")", type
        else:
            # Variable or constant
            return var_or_const()


def assign():
    """
    Generates a random assignment expression.
    """
    exp_str, type = expression()
    return " = " + exp_str, type


def var_decl(struct_like=False, struct_name=None, event_type=None):
    """
    Generates a random variable declaration.
    """
    global VAR_CNT
    id = var_id()
    type_id = get_type()
    decl = type_id + " " + id
    # Assign value
    if(random.randint(0, 1) and not struct_like):
        exp_str, type = assign()
        decl += exp_str

    if(not struct_like):
        LIST_OF_VARS[SCOPE_CNT].append({"name": id, "type": type_id})
        VAR_CNT += 1
    else:     
        if(struct_name not in DICT_OF_STRUCTS):
            DICT_OF_STRUCTS[struct_name] = []
        DICT_OF_STRUCTS[struct_name].append({"name": id, "type": type_id})

        if(struct_like == EVENT):
            if(struct_name not in DICT_OF_EV_DECL[event_type]):
                DICT_OF_EV_DECL[event_type][struct_name] = []
                DICT_OF_EV_EP[struct_name] = []
            DICT_OF_EV_DECL[event_type][struct_name].append({"name": id, "type": type_id})
    return decl + ";"

def struct_inst_decl():
    """
    Generates a random struct instance declaration.
    """
    global VAR_CNT
    if(len(STRUCT_PKT_BP_IDS) == 0):
        return None

    struct_name = random.choice(STRUCT_PKT_BP_IDS)
    id = var_id()
    decl = struct_name + " " + id + ";"

    LIST_OF_VARS[SCOPE_CNT].append({"name": id, "type": struct_name})
    VAR_CNT += 1

    for entry in DICT_OF_STRUCTS[struct_name]:
        LIST_OF_VARS[SCOPE_CNT].append({"name": id + "." + entry["name"], "type": entry["type"]})
        VAR_CNT += 1

    return decl

def return_statement():
    """
    Generates a random return statement.
    """
    if(CURR_EP_RETURN_TYPE == "void"):
        return "return;"
    elif(CURR_EP_RETURN_TYPE == "list<instr_t>"):
        var_id = catch_var_id("list<instr_t>")[0]
        if(var_id == None):
            return "PROBLEM"
        return "return " + var_id + ";"
    if(random.randint(0, 1) and len(LIST_OF_VARS) and VAR_CNT > 0):
        return "return " + catch_var_id()[0] + assign() + ";"
    exp_str, type = expression()
    return "return " + exp_str + ";"


def for_statement():
    """
    Generates a random for loop statement.
    """
    global SCOPE_CNT
    first_arg = ""
    if(random.randint(0, 1) and len(LIST_OF_VARS) > 0 and VAR_CNT > 0):
        exp_str_1, type_1 = catch_var_id()
        exp_str_2, type_2 = assign()
        first_arg = exp_str_1 + exp_str_2 + ";"
    else:
        first_arg = var_decl()
    second_arg_str, second_arg_type = expression()

    third_arg_str_1, third_arg_type_1 = catch_var_id()
    third_arg_str_2, third_arg_type_2 = assign()
    for_stmt = "for(" + first_arg + " " + second_arg_str + "; " + third_arg_str_1 + third_arg_str_2 + ") {\n"
    SCOPE_CNT += 1
    for_stmt += statements()
    SCOPE_CNT -= 1
    for_stmt += indentation() + "}"

    return indentation() + for_stmt

def while_statement():
    """
    Generates a random while loop statement.
    """
    global SCOPE_CNT
    exp_str, type = expression()
    while_stmt = "while(" + exp_str + ") {\n"
    SCOPE_CNT += 1
    while_stmt += statements()
    SCOPE_CNT -= 1
    while_stmt += indentation() + "}"

    return indentation() + while_stmt

def condition_statement():
    """
    Generates a random conditional statement.
    """
    global SCOPE_CNT
    exp_str, type = expression()
    cond_stmt = "if(" + exp_str + ") {\n"
    SCOPE_CNT += 1
    cond_stmt += statements()
    SCOPE_CNT -= 1
    cond_stmt += indentation() + "}"

    for _ in range(random.randint(0, 2)):
        exp_str, type = expression()
        cond_stmt += "\n" + indentation() + "else if(" + exp_str + ") {\n"
        SCOPE_CNT += 1
        cond_stmt += statements()
        SCOPE_CNT -= 1
        cond_stmt += indentation() + "}"
    
    if(random.randint(0, 1)):
        cond_stmt += "\n" + indentation() + "else {\n"
        SCOPE_CNT += 1
        cond_stmt += statements()
        SCOPE_CNT -= 1
        cond_stmt += indentation() + "}"

    return indentation() + cond_stmt

def statements():
    """
    Generates a random sequence of statements.
    """
    global VAR_CNT

    LIST_OF_VARS.append([])

    total_statements = ""

    MAX_ITER = 5
    if(SCOPE_CNT < 3):
        for i in range(random.randint(1, MAX_ITER)):
            REPEAT = False
            stmt_num = random.randint(0, 6)

            if(stmt_num == 6):
                if(i >= MAX_ITER - 1):
                    total_statements += indentation() + return_statement() + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 5 and len(LIST_OF_VARS) and VAR_CNT > 0):
                exp_str_1, type_1 = catch_var_id()
                exp_str_2, type_2 = assign()
                total_statements += indentation() + exp_str_1 + exp_str_2 + "\n"
            elif(stmt_num == 4):
                total_statements += indentation() + var_decl() + "\n"
            elif(stmt_num == 3):
                struct_decl_stmt = struct_inst_decl()
                if(struct_decl_stmt != None):
                    total_statements += indentation() + struct_decl_stmt + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 2):
                for_stmt = for_statement()
                if(for_stmt != None):
                    total_statements += for_stmt + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 1):
                while_stmt = while_statement()
                if(while_stmt != None):
                    total_statements += while_stmt + "\n"
                    continue
                REPEAT = True
            else:
                cond_stmt = condition_statement()
                if(cond_stmt != None):
                    total_statements += cond_stmt + "\n"
                    continue
                REPEAT = True

            if(REPEAT):
                i -= 1
    else:
        for i in range(random.randint(1, MAX_ITER)):
            REPEAT = False
            stmt_num = random.randint(0, 3)
            if(stmt_num == 3):
                if(i >= MAX_ITER - 1):
                    total_statements += indentation() + return_statement() + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 2 and len(LIST_OF_VARS) and VAR_CNT > 0):
                exp_str_1, type_1 = catch_var_id()
                exp_str_2, type_2 = assign()
                total_statements += indentation() + exp_str_1 + exp_str_2 + "\n"
            elif(stmt_num == 1):
                total_statements += indentation() + struct_inst_decl() + "\n"
            elif(stmt_num == 0):
                total_statements += indentation() + var_decl() + "\n"

            if(REPEAT):
                i -= 1

    VAR_CNT -= len(LIST_OF_VARS[-1])
    LIST_OF_VARS.pop()
    return total_statements

def ep_decl():
    """
    Generates a random event processor declaration.
    """
    global SCOPE_CNT, CURR_EP_RETURN_TYPE, VAR_CNT
    ep_decl = ""

    for event_name in DICT_OF_EV_EP.keys():
        for _ in range(random.randint(1, 3)):

            returns_instr = random.randint(0, 1)
            if(returns_instr):
                ep_decl += "list<instr_t> "
                CURR_EP_RETURN_TYPE = "list<instr_t>"
            else:
                ep_decl += "void "
                CURR_EP_RETURN_TYPE = "void"

            ep_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')
            DICT_OF_EV_EP[event_name].append(ep_name)
            ep_decl += ep_name + "(" + event_name + " ev, " + CONTEXT_NAME + " ctx, " + SCRATCH_NAME +" scratch){\n"

            SCOPE_CNT += 1
            LIST_OF_VARS.append([{"name": "ev", "type": event_name},
                                 {"name": "ctx", "type": CONTEXT_NAME},
                                 {"name": "scratch", "type": SCRATCH_NAME}])
            
            # TODO: maybe add a randomized list<instr_t> variable declaration 
            if(returns_instr):
                LIST_OF_VARS[-1].append({"name": "out", "type": "list<instr_t>"})
                ep_decl += indentation() + "list<instr_t> out;\n"
                VAR_CNT += 1 

            VAR_CNT += 3            
            ep_decl += statements()
            VAR_CNT -= 3

            if(returns_instr):
                VAR_CNT -= 1 

            SCOPE_CNT -= 1
            ep_decl += "}\n\n"
    return ep_decl

def struct_decl():
    """
    Generates a random struct declaration.
    """
    global SCOPE_CNT
    struct_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    struct_decl = "struct " + struct_name + " {\n"
    SCOPE_CNT += 1

    STRUCT_PKT_BP_IDS.append(struct_name)

    for _ in range(random.randint(1, 8)):
        struct_decl += indentation() + var_decl(STRUCT, struct_name) + "\n"

    SCOPE_CNT -= 1
    struct_decl += indentation() + "}\n"
    return struct_decl

def event_decl():
    """
    Generates a random event declaration.
    """
    global SCOPE_CNT
    event_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    event_type = random.choice(list(DICT_OF_EV_DECL.keys()))

    ev_decl = "event " + event_name + " : " + event_type + " {\n"
    SCOPE_CNT += 1

    for _ in range(random.randint(1, 8)):
        ev_decl += indentation() + var_decl(EVENT, event_name, event_type) + "\n"

    SCOPE_CNT -= 1
    ev_decl += indentation() + "}\n"
    return ev_decl

def context_decl():
    """
    Generates a random context declaration.
    """
    global SCOPE_CNT, CONTEXT_NAME
    ctx_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    context_decl = "context " + ctx_name + " {\n"
    SCOPE_CNT += 1

    for _ in range(random.randint(1, 15)):
        context_decl += indentation() + var_decl(STRUCT, ctx_name) + "\n"

    SCOPE_CNT -= 1
    context_decl += indentation() + "}\n"

    CONTEXT_NAME = ctx_name
    return context_decl

def scratch_decl():
    """
    Generates a random scratchpad declaration.
    """
    global SCOPE_CNT, SCRATCH_NAME
    scratch_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    scratch_decl = "scratchpad " + scratch_name + " {\n"
    SCOPE_CNT += 1

    for _ in range(random.randint(1, 5)):
        scratch_decl += indentation() + var_decl(STRUCT, scratch_name) + "\n"

    SCOPE_CNT -= 1
    scratch_decl += indentation() + "}\n"

    SCRATCH_NAME = scratch_name
    return scratch_decl

def pkt_bp_decl():
    """
    Generates a random packet blueprint declaration.
    """
    global SCOPE_CNT
    pkt_bp_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    pkt_bp_decl = "pkt_bp " + pkt_bp_name + " {\n"
    SCOPE_CNT += 1

    STRUCT_PKT_BP_IDS.append(pkt_bp_name)

    for _ in range(random.randint(1, 10)):
        pkt_bp_decl += indentation() + var_decl(STRUCT, pkt_bp_name) + "\n"
    
    pkt_bp_decl += indentation() + "data_t data;" + "\n"
    DICT_OF_STRUCTS[pkt_bp_name].append({"name": "data", "type": "data_t"})

    SCOPE_CNT -= 1
    pkt_bp_decl += indentation() + "}\n"
    return pkt_bp_decl

def dispatcher_decl():
    """
    Generates a random dispatcher declaration.
    """
    global SCOPE_CNT
    dispatcher_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')
    disp_decl = "dispatch " + dispatcher_name + " {\n"
    SCOPE_CNT += 1
    for event_name in DICT_OF_EV_EP.keys():
        ep_chain = ""
        first = True
        for ep_name in DICT_OF_EV_EP[event_name]:
            if(not first):
                ep_chain += ", "
            ep_chain += ep_name
            first = False
        disp_decl += indentation() + event_name + " -> {" + ep_chain + "};\n"

    SCOPE_CNT -= 1
    disp_decl += "}\n"
    return disp_decl


def generator():
    with open("generated_program.mtp", "w") as f:
        for _ in range(random.randint(1, 3)):
            f.write(struct_decl())
        for _ in range(random.randint(3, 5)):
            f.write(event_decl())
        f.write(context_decl())
        f.write(scratch_decl())
        f.write(pkt_bp_decl())
        for _ in range(random.randint(3, 5)):
            f.write(ep_decl())
        f.write(dispatcher_decl())


if __name__=="__main__":
    generator()