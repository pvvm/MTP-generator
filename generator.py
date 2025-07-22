import sys
import random
import rstr
from functions_mtp import *
from methods_mtp import method_call
from error_gen import generate_error

# TODO: fix sliding_wnd methods. They aren't finding sliding window variables (there's one default in ctx)
# TODO: add a way to different EPs to be shared between events
# TODO: maybe we should send a list with the types of the variables we want from var_or_const.
#       This will also be important to check the different kinds of int

ARGUMENTS = ["-lex", "-syn", "-sem"]
LEX_FLAG = False
SYN_FLAG = False
SEM_FLAG = False


STRUCT = 1
EVENT = 2

IN_EP = False

SCOPE_CNT = 0

#INT_TYPE = ["int8", "int16", "int32", "int64"]
INT_TYPE = ["int"]
FLOAT_TYPE = ["float"]
BOOL_TYPE = ["bool"]
LIST_TYPE = ["list"]
ADDR_TYPE = ["addr_t"]
DATA_TYPE = ["data_t"]
CHECKSUM_TYPE = ["checksum16_t"]
INSTR_TYPE = ["instr_t"]
FLOW_TYPE = ["flow_id"]
ALL_TYPES = INT_TYPE + FLOAT_TYPE + BOOL_TYPE + LIST_TYPE + ADDR_TYPE + DATA_TYPE + CHECKSUM_TYPE + INSTR_TYPE + FLOW_TYPE

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
PKT_BP_ID = ""


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

# Type of the event that the current event processor processes.
CURR_EP_EVENT_TYPE = ""

# Type of the value returned by the current event processor.
CURR_EP_RETURN_TYPE = ""

# Name of the context and scratchpad used in the code.
CONTEXT_NAME = ""
SCRATCH_NAME = ""

def indentation():
    """
    Returns a string with the current indentation level.
    """
    return "\t" * (SCOPE_CNT + (1 if IN_EP else 0))

def get_type(no_list=False):
    """
    Generates a random type declaration.
    """
    if(no_list):
        return random.choice(INT_TYPE + FLOAT_TYPE + BOOL_TYPE + ADDR_TYPE + DATA_TYPE + CHECKSUM_TYPE + INSTR_TYPE + FLOW_TYPE)
    return random.choice(ALL_TYPES)

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

def catch_var_id(var_type=None, list_of_vars=LIST_OF_VARS):
    if(SEM_FLAG and random.randint(0, 100) == 0):
        teste = var_id()
        #print(teste)
        return teste, "SEM_FLAG"

    index = 0
    if var_type == None or var_type == "SEM_FLAG":
        while True:
            index = random.randint(0, len(list_of_vars) - 1)
            if(len(list_of_vars[index]) > 0):
                break
        random_var = random.choice(list_of_vars[index])
        struct_id = random_var["type"]
        # Check if the variable is a struct-like variable
        if(struct_id in DICT_OF_STRUCTS):
            return catch_struct_value(struct_id, DICT_OF_STRUCTS[struct_id])
        return random_var["name"], random_var["type"]
    
    list_vars = []
    # List containing the types of variables "list"
    list_list_type = []
    for entry in list_of_vars:
        for var in entry:
            if(var_type == "list" and "list<" in var["type"]):
                list_vars.append(var["name"])
                list_list_type.append(var["type"])
            elif(var["type"] == var_type):
                list_vars.append(var["name"])

    if(list_vars == []):
        return None, var_type
    
    if(var_type == "list"):
        index = random.randint(0, len(list_vars) - 1)
        return list_vars[index], list_list_type[index]

    random_var = random.choice(list_vars)
    return random_var, var_type

def var_or_const(var_type=None, list_of_vars=LIST_OF_VARS):
    """
    Returns a variable or a random constant.
    """
    if((random.randint(0, 2) < 2 and len(list_of_vars) > 0 and VAR_CNT > 0)
       or var_type not in ["int", "float", "bool"]):
        return_var, return_type = catch_var_id(var_type, list_of_vars)
        if(return_var == None):
            return "", "NO_ARG_FLAG"
        return return_var, return_type
    else:
        # Generate a random constant
        ran = random.randint(0, 2)
        if(ran == 2 or var_type == "int"):
            return rstr.xeger(r'[0-9]{1,10}'), "int"
        elif(ran == 1 or var_type == "float"):
            return rstr.xeger(r'[0-9]{1,10}[.][0-9]{1,5}'), "float"
        elif(ran == 0 or var_type == "bool"):
            return random.choice(["true", "false"]), "bool"

def expression(max_depth, expected_type=None):
    """
    Generates a random expression.
    """
    #if(expected_type != None and "list<" in expected_type):
    #    expected_type = expected_type.split("<")[1].split(">")[0]
    #print(expected_type)
    if(expected_type in ["void", "flow_id", "checksum16_t", "data_t", "instr_t"]):
        return function_call(expected_type, PKT_BP_ID, DICT_OF_STRUCTS, CURR_EP_EVENT_TYPE, CONTEXT_NAME, LIST_OF_VARS)
    elif(expected_type in ["addr_t"] or
        (expected_type != None and expected_type.split("<")[0] == "list")):
        return "", "NO_ARG_FLAG"

    if(max_depth <= 0):
        return var_or_const(expected_type)
    max_depth -= 1

    rnd_num = random.randint(0, 3)
    if(rnd_num == 3):
        # Binary operation
        exp_str_1, type_1 = var_or_const(expected_type)
        exp_str_2, type_2 = expression(max_depth, expected_type)
        operation = random.choice(BINARY_OPS)
        if(type_1 not in ["int", "float", "bool"] or type_2 not in ["int", "float", "bool"]):
            # TODO: maybe we should send a list with the types of the variables we want from var_or_const
            return var_or_const(expected_type)
        if(operation in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]):
            return exp_str_1 + " " + operation + " " + exp_str_2, "bool"
        if(type_1 == "float" or type_2 == "float"):
            return exp_str_1 + " " + operation + " " + exp_str_2, "float"
        return exp_str_1 + " " + operation + " " + exp_str_2, "int"
    elif(rnd_num == 2):
        # Unary operation
        exp_str, type = expression(max_depth, expected_type)
        if(type not in ["int", "float", "bool"]):
            # TODO: maybe we should send a list with the types of the variables we want from var_or_const
            return var_or_const(expected_type)
        return random.choice(UNARY_OPS) + " " + exp_str, type
    elif(rnd_num == 1):
        # Nested expression
        exp_str, type = expression(max_depth, expected_type)
        return "( " + exp_str + " )", type
    else:
        # Variable or constant
        return var_or_const(expected_type)


def assign(expected_type=None):
    """
    Generates a random assignment expression.
    """ 
    max_depth = random.randint(1, 10)
    exp_str, type = expression(max_depth, expected_type)
    #if(exp_str == ""):
    #    print("TYPE:", type)
    if(type == "NO_ARG_FLAG" and not SEM_FLAG):
        return "", type
    return " = " + exp_str, type


def var_decl(struct_like=False, struct_name=None, event_type=None, required_type=None):
    """
    Generates a random variable declaration.
    """
    global VAR_CNT
    id = var_id()
    if(required_type == None):
        type_id = get_type()
    else:
        type_id = required_type
    if(type_id == "list"):
        type_id = "list<" + get_type(True) + ">"
    decl = type_id + " " + id
    # Assign value
    if(random.randint(0, 1) and not struct_like):
        exp_str, type = assign(type_id)
        decl += exp_str

    if(not struct_like):
        LIST_OF_VARS[SCOPE_CNT - 1].append({"name": id, "type": type_id})
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
    return decl + " ;"

def struct_inst_decl():
    """
    Generates a random struct instance declaration.
    """
    global VAR_CNT
    if(len(STRUCT_PKT_BP_IDS) == 0):
        return None

    struct_name = random.choice(STRUCT_PKT_BP_IDS)
    id = var_id()
    decl = struct_name + " " + id + " ;"

    LIST_OF_VARS[SCOPE_CNT - 1].append({"name": id, "type": struct_name})
    VAR_CNT += 1

    for entry in DICT_OF_STRUCTS[struct_name]:
        LIST_OF_VARS[SCOPE_CNT - 1].append({"name": id + "." + entry["name"], "type": entry["type"]})
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
        return "return " + var_id + " ;"
    if(random.randint(0, 1) and len(LIST_OF_VARS) and VAR_CNT > 0):
        exp_str, type = catch_var_id()
        return "return " + exp_str + assign(type) + " ;"
    exp_str, type = expression(random.randint(1, 10))
    return "return " + exp_str + " ;"


def for_statement():
    """
    Generates a random for loop statement.
    """
    global SCOPE_CNT, VAR_CNT
    first_arg = ""
    if(random.randint(0, 1) and len(LIST_OF_VARS) > 0 and VAR_CNT > 0):
        exp_str_1, type_1 = catch_var_id(var_type="int")
        if(exp_str_1 == None):
            return None
        SCOPE_CNT += 1
        LIST_OF_VARS.append([])
        exp_str_2, type_2 = assign(type_1)
        first_arg = exp_str_1 + exp_str_2 + ";"
    else:
        SCOPE_CNT += 1
        LIST_OF_VARS.append([])
        first_arg = var_decl(required_type="int")
    second_arg_str, second_arg_type = expression(random.randint(1, 10), expected_type="bool")

    third_arg_str_1, third_arg_type_1 = catch_var_id(var_type="int")
    third_arg_str_2, third_arg_type_2 = assign(third_arg_type_1)
    for_stmt = "for ( " + first_arg + " " + second_arg_str + " ; " + third_arg_str_1 + third_arg_str_2 + " ) {\n"
    
    for_stmt += statements()
    SCOPE_CNT -= 1
    for_stmt += indentation() + "}"

    VAR_CNT -= len(LIST_OF_VARS[-1])
    LIST_OF_VARS.pop()

    return indentation() + for_stmt

def while_statement():
    """
    Generates a random while loop statement.
    """
    global SCOPE_CNT, VAR_CNT
    LIST_OF_VARS.append([])
    SCOPE_CNT += 1
    while True:
        exp_str, type = expression(random.randint(1, 10), expected_type="int")
        if(exp_str != ""):
            break
    while_stmt = "while ( " + exp_str + " ) {\n"
    while_stmt += statements()
    SCOPE_CNT -= 1
    while_stmt += indentation() + "}"

    VAR_CNT -= len(LIST_OF_VARS[-1])
    LIST_OF_VARS.pop()

    return indentation() + while_stmt

def condition_statement():
    """
    Generates a random conditional statement.
    """
    global SCOPE_CNT, VAR_CNT
    while True:
        exp_str, type = expression(random.randint(1, 10), expected_type="int")
        if(exp_str != ""):
            break
    cond_stmt = "if ( " + exp_str + " ) {\n"
    SCOPE_CNT += 1
    LIST_OF_VARS.append([])
    cond_stmt += statements()
    SCOPE_CNT -= 1
    cond_stmt += indentation() + "}"

    VAR_CNT -= len(LIST_OF_VARS[-1])
    LIST_OF_VARS.pop()

    for _ in range(random.randint(0, 2)):
        while True:
            exp_str, type = expression(random.randint(1, 10), expected_type="int")
            if(exp_str != ""):
                break
        cond_stmt += "\n" + indentation() + "else if ( " + exp_str + " ) {\n"
        SCOPE_CNT += 1
        LIST_OF_VARS.append([])
        cond_stmt += statements()
        SCOPE_CNT -= 1
        cond_stmt += indentation() + "}"

        VAR_CNT -= len(LIST_OF_VARS[-1])
        LIST_OF_VARS.pop()
    
    if(random.randint(0, 1)):
        cond_stmt += "\n" + indentation() + "else {\n"
        SCOPE_CNT += 1
        LIST_OF_VARS.append([])
        cond_stmt += statements()
        SCOPE_CNT -= 1
        cond_stmt += indentation() + "}"

        VAR_CNT -= len(LIST_OF_VARS[-1])
        LIST_OF_VARS.pop()

    return indentation() + cond_stmt

def statements(default_vars=[]):
    """
    Generates a random sequence of statements.
    """
    #global VAR_CNT

    #LIST_OF_VARS.append(default_vars)
    #VAR_CNT += len(default_vars)

    total_statements = ""

    MAX_ITER = 10
    if(SCOPE_CNT < 3):
        for i in range(random.randint(1, MAX_ITER)):
            REPEAT = False
            stmt_num = random.randint(0, 7)

            if(stmt_num == 7):
                method_stmt = method_call(LIST_OF_VARS)
                if(method_stmt != None):
                    total_statements += indentation() + method_stmt + " ;\n"
                    continue
                REPEAT = True
            elif(stmt_num == 6):
                if(i >= MAX_ITER - 1):
                    total_statements += indentation() + return_statement() + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 5 and len(LIST_OF_VARS) and VAR_CNT > 0):
                exp_str_1, type_1 = catch_var_id()
                exp_str_2, type_2 = assign(type_1)
                total_statements += indentation() + exp_str_1 + exp_str_2 + " ;\n"
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
            stmt_num = random.randint(0, 4)
            if(stmt_num == 4):
                method_stmt = method_call(LIST_OF_VARS)
                if(method_stmt != None):
                    total_statements += indentation() + method_stmt + " ;\n"
                    continue
                REPEAT = True
            elif(stmt_num == 3):
                if(i >= MAX_ITER - 1):
                    total_statements += indentation() + return_statement() + "\n"
                    continue
                REPEAT = True
            elif(stmt_num == 2 and len(LIST_OF_VARS) and VAR_CNT > 0):
                exp_str_1, type_1 = catch_var_id()
                exp_str_2, type_2 = assign(type_1)
                total_statements += indentation() + exp_str_1 + exp_str_2 + " ;\n"
            elif(stmt_num == 1):
                total_statements += indentation() + struct_inst_decl() + "\n"
            elif(stmt_num == 0):
                total_statements += indentation() + var_decl() + "\n"

            if(REPEAT):
                i -= 1

    #VAR_CNT -= len(LIST_OF_VARS[-1])
    #LIST_OF_VARS.pop()
    return total_statements

def ep_decl():
    """
    Generates a random event processor declaration.
    """
    global SCOPE_CNT, CURR_EP_EVENT_TYPE, CURR_EP_RETURN_TYPE, VAR_CNT, IN_EP, VAR_CNT
    ep_decl = ""
    IN_EP = True

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
            ep_decl += ep_name + "( " + event_name + " ev , " + CONTEXT_NAME + " ctx , " + SCRATCH_NAME +" scratch ) {\n"

            CURR_EP_EVENT_TYPE = event_name

            SCOPE_CNT += 1
            LIST_OF_VARS.append([{"name": "ev", "type": event_name},
                                 {"name": "ctx", "type": CONTEXT_NAME},
                                 {"name": "scratch", "type": SCRATCH_NAME}])
            
            #list_default_vars = [{"name": "ev", "type": event_name},
            #                     {"name": "ctx", "type": CONTEXT_NAME},
            #                     {"name": "scratch", "type": SCRATCH_NAME}]
            
            # TODO: maybe add a randomized list<instr_t> variable declaration 
            if(returns_instr):
                LIST_OF_VARS[-1].append({"name": "out", "type": "list<instr_t>"})
                #list_default_vars += [{"name": "out", "type": "list<instr_t>"}]
                ep_decl += indentation() + "list<instr_t> out ;\n"
                VAR_CNT += 1 

            VAR_CNT += 3         
            ep_decl += statements()
            VAR_CNT -= len(LIST_OF_VARS[-1])
            LIST_OF_VARS.pop()

            #if(returns_instr):
            #    VAR_CNT -= 1 

            SCOPE_CNT -= 1
            ep_decl += "}\n\n"

    IN_EP = False
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

    # Special declaration of sliding window
    context_decl += indentation() + var_decl(STRUCT, ctx_name, required_type="sliding_wnd") + "\n"

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
    global SCOPE_CNT, PKT_BP_ID
    pkt_bp_name = rstr.xeger(r'[A-Z][a-zA-Z0-9_]{0,10}')

    pkt_bp_decl_stmt = "pkt_bp " + pkt_bp_name + " {\n"
    SCOPE_CNT += 1

    STRUCT_PKT_BP_IDS.append(pkt_bp_name)
    PKT_BP_ID = pkt_bp_name

    for _ in range(random.randint(1, 10)):
        pkt_bp_decl_stmt += indentation() + var_decl(STRUCT, pkt_bp_name) + "\n"
    
    pkt_bp_decl_stmt += indentation() + "data_t data ;" + "\n"
    DICT_OF_STRUCTS[pkt_bp_name].append({"name": "data", "type": "data_t"})

    SCOPE_CNT -= 1
    pkt_bp_decl_stmt += indentation() + "}\n"
    return pkt_bp_decl_stmt

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
        disp_decl += indentation() + event_name + " -> { " + ep_chain + " } ;\n"

    SCOPE_CNT -= 1
    disp_decl += "}\n"
    return disp_decl


def generator():
    global LEX_FLAG, SYN_FLAG, SEM_FLAG
    for i in range(1, len(sys.argv)):
        if(sys.argv[i] not in ARGUMENTS):
            print("Invalid argument: " + sys.argv[i])
            exit(1)
        if(sys.argv[i] == "-lex"):
            LEX_FLAG = True
        elif(sys.argv[i] == "-syn"):
            SYN_FLAG = True
        elif(sys.argv[i] == "-sem"):
            SEM_FLAG = True

    output = ""
    with open("generated_program.mtp", "w") as f:
        for _ in range(random.randint(1, 3)):
            output += struct_decl()
        for _ in range(random.randint(3, 5)):
            output += event_decl()
        output += context_decl()
        output += scratch_decl()
        output += pkt_bp_decl()
        for _ in range(random.randint(3, 5)):
            output += ep_decl()
        output += dispatcher_decl()

        if(LEX_FLAG or SYN_FLAG):
            f.write(generate_error(output, LEX_FLAG, SYN_FLAG))
        else:
            f.write(output)
    #print(LIST_OF_VARS, VAR_CNT)


if __name__=="__main__":
    generator()