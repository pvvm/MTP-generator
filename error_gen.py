import random
import rstr

def invalid_token():
    """
    Generates a random invalid token.
    """
    return rstr.xeger(r'[^\s\n\t{}\[\]\(\)\+\-\*/%=<>;:.,\!&\|\^A-Za-z0-9_]{1,5}')

def valid_token():
    """
    Generates a random valid token.
    """
    return rstr.xeger(r'[{}\[\]\(\)\+\-\*/%=<>;:.,\!&]|\b(?:while|for|if|else|return)\b|[A-Za-z_][A-Za-z0-9_]{0,10}')

def insert_token(indentation, split_line, LEX_FLAG, SYN_FLAG):
    """
    Inserts a random token into the line.
    """
    random_index = random.randint(0, len(split_line) - 1)
    if(LEX_FLAG):
        split_line.insert(random_index, invalid_token())
    if(SYN_FLAG):
        split_line.insert(random_index, valid_token())
    return "\t" * indentation + " ".join(split_line)


def remove_token(indentation, split_line):
    """
    Removes a random token from the line.
    """
    random_token = random.randint(0, len(split_line) - 1)
    split_line.pop(random_token)
    return "\t" * indentation + " ".join(split_line)
    

def generate_error(program_str, LEX_FLAG, SYN_FLAG):
    """
    Iterates over the generated program to insert random errors.
    """
    lines = program_str.splitlines()
    for i in range(0, len(lines) - 1):
        if lines[i].strip() == "":
            continue
        random_num = random.randint(0, 100)
        indentation = len(lines[i]) - len(lines[i].lstrip('\t'))
        split_line = lines[i].split()

        # Randomly removes a token in the line
        if(random_num == 0 and SYN_FLAG):
            #print(lines[i])
            lines[i] = remove_token(indentation, split_line)
            #print(lines[i])

        # Randomly adds a token in the line
        elif(random_num == 1):
            #print(lines[i])
            lines[i] = insert_token(indentation, split_line, LEX_FLAG, SYN_FLAG)
            #print(lines[i])

    return "\n".join(lines)