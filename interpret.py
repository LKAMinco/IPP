import argparse
import re
import sys
import xml.etree.ElementTree as et
import os
from interpret_class import Stack, Instruction, Variable

argp = argparse.ArgumentParser()
argp.add_argument('-s', '--source', metavar='FILE', help='Redirect source from stdin to SOURCE')
argp.add_argument('-i', '--input', metavar='FILE', help='Redirect input from stdin to INPUT')

args = argp.parse_args()



def writeErr(code, message=''):
    sys.stderr.write(message + '\n')
    exit(code)


source_file = sys.stdin
input_file = sys.stdin

if args.source is None and args.input is None:
    writeErr(10, 'Insufficient number of parameters')

if args.source is not None:
    if os.path.exists(args.source):
        try:
            source_file = args.source
        except (OSError, MemoryError):
            writeErr(11, 'Can not open source file')
    else:
        writeErr(11, 'Can not locate source file')

if args.input is not None:
    if os.path.exists(args.input):
        try:
            input_file = open(args.input, 'r')
        except:
            writeErr(11, 'Can not open input file')
    else:
        writeErr(11, 'Can not locate source file')

try:
    tree = et.parse(source_file)
    root = tree.getroot()

    if root.tag != 'program' and root.attrib['language'] != 'IPPcode22':
        writeErr(31, 'Wrong XML format')
    elif len(root.attrib) == 2 and ('name' not in root.attrib and 'description' not in root.attrib):
        writeErr(31, 'Wrong XML format')
    elif len(root.attrib) == 3 and ('name' not in root.attrib or 'description' not in root.attrib):
        writeErr(31, 'Wrong XML format')
    elif len(root.attrib) > 3:
        writeErr(31, 'Wrong XML format')

    instruction = []
    index = 0
    labels = {}
    for child in root:
        if child.tag != 'instruction':
            writeErr(32, 'Unexpected element')
        if not ('opcode' in child.attrib.keys()) or not ('order' in child.attrib.keys()):
            writeErr(32, 'Missing argument in element')
        if len(child.attrib.keys()) > 2:
            writeErr(31, 'Too many argument in element')
        try:
            int(child.attrib['order'])
        except:
            writeErr(32, 'Wrong order')
        if int(child.attrib['order']) < 1:
            writeErr(32, 'Wrong order')
        instruction.append(Instruction(child.attrib['opcode'].upper(), child.attrib['order']))
        for arg in child:
            instruction[index].addArgument(arg.attrib['type'], arg.text, arg.tag)
        instruction[index].args.sort(key=lambda x: x.arg_order)
        instruction[index].checkOrdOfArgs()
        index += 1
except Exception as e:
    if e == 32:
        writeErr(32, 'Wrong format of element')
    else:
        writeErr(31, 'Wrong XML format')

instruction.sort(key=lambda x: int(x.order))
for x in range(0, len(instruction)):
    instruction[x].my_order = x + 1
    if len(instruction) != 1:
        if instruction[x].order == instruction[x - 1].order:
            writeErr(32, 'Instructions with same order found')
    if instruction[x].name == 'LABEL':
        if instruction[x].args[0].value in labels:
            writeErr(52, 'Duplicated label')
        labels[instruction[x].args[0].value] = x


def getFloat(value):
    try:
        return float(value).hex()
    except:
        try:
            return float.fromhex(value).hex()
        except:
            return ''


def convertString(string):
    convert = re.findall('(?<=\\\)[0-9]{3}', string)
    for x in convert:
        string = re.sub('\\\[0-9]{3}', chr(int(x)), string, 1)
    return string


def checkFrame(frame):
    if frame == 'GF':
        return 'g_frame' in globals()
    elif frame == 'TF':
        return 't_frame' in globals()
    elif frame == 'LF':
        return 'l_frame' in globals()
    else:
        writeErr(54, 'Frame does not exiss')


def checkVarA(variable):
    frame = re.split('@', variable)
    if checkFrame(frame[0]) and frame[0] == 'GF':
        return variable in g_frame
    elif checkFrame(frame[0]) and frame[0] == 'TF':
        return variable in t_frame
    elif checkFrame(frame[0]) and frame[0] == 'LF':
        return variable in l_frame
    else:
        writeErr(55, 'Can not locate variable in current frame')


def checkVar(variable):
    if checkVarA(variable):
        return True
    else:
        writeErr(54, 'Can not locate variable in frame')


def checkConst(const):
    if const.type == 'string':
        if const.value is None:
            return ''
        else:
            return convertString(const.value)
    elif const.type == 'int':
        try:
            return int(const.value)
        except:
            writeErr(32, 'Wrong value constant')
    elif const.type == 'bool':
        if const.value.lower() == 'true' or const.value.lower() == 'false':
            return const.value.lower()
        else:
            writeErr(32, 'Wrong value constant')
    elif const.type == 'nil':
        if const.value == 'nil':
            return ''
        else:
            writeErr(32, 'Wrong value constant')
    elif const.type == 'float':
        return getFloat(const.value)
    else:
        writeErr(54, 'Wrong type of constant')


def getType(variable):
    checkVar(variable)
    frame = re.split('@', variable)
    if checkVar(variable):
        if frame[0] == 'GF':
            g_frame[variable].updateVar()
            return g_frame[variable].type
        elif frame[0] == 'LF':
            l_frame[variable].updateVar()
            return l_frame[variable].type
        elif frame[0] == 'TF':
            t_frame[variable].updateVar()
            return t_frame[variable].type
    else:
        writeErr(54, 'VWrong frame sepecific')


def getValueA(variable):
    frame = re.split('@', variable)
    if checkVar(variable):
        if frame[0] == 'GF':
            g_frame[variable].updateVar()
            return g_frame[variable].value
        elif frame[0] == 'LF':
            l_frame[variable].updateVar()
            return l_frame[variable].value
        elif frame[0] == 'TF':
            t_frame[variable].updateVar()
            return t_frame[variable].value
    else:
        writeErr(54, 'Var is not defined in the frame')


def getValue(variable):
    if getValueA(variable) is not None:
        return getValueA(variable)
    else:
        writeErr(56, 'Missing value of variable')


def putValue(variable, value, type):
    checkVar(variable)
    frame = re.split('@', variable)
    if checkVar(variable):
        if type == 'int':
            value = int(value)
        if frame[0] == 'GF':
            g_frame[variable].value = value
            g_frame[variable].type = type
        elif frame[0] == 'LF':
            l_frame[variable].value = value
            l_frame[variable].type = type
        elif frame[0] == 'TF':
            t_frame[variable].value = value
            t_frame[variable].type = type
    else:
        writeErr(54, 'Var is not defined in the frame')


def doMath(operation, a, b, is_float): # mathematical operations
    if is_float:
        a = float().fromhex(getFloat(a))
        b = float().fromhex(getFloat(b))
    else:
        a = int(a)
        b = int(b)
    if operation == 'ADD' or operation == 'ADDS':
        return a + b
    elif operation == 'SUB' or operation == 'SUBS':
        return a - b
    elif operation == 'MUL' or operation == 'MULS':
        return a * b
    elif operation == 'IDIV' or operation == 'IDIVS':
        if a != 0 and b != 0:
            return a // b
        else:
            writeErr(57, 'Divide by zero')
    elif operation == 'DIV' or operation == 'DIVS':
        if a != 0 and b != 0:
            return a / b
        else:
            writeErr(57, 'Divide by zero')


def doCompare(operation, a, b): #compare operation
    if operation == 'LT' or operation == 'LTS':
        return a < b
    elif operation == 'GT' or operation == 'GTS':
        return a > b
    elif operation == 'EQ' or operation == 'EQS':
        return a == b


def doLogic(operation, a, b): #logic operations
    if operation == 'AND' or operation == 'ANDS':
        return a and b
    elif operation == 'OR' or operation == 'ORS':
        return a or b
    elif operation == 'NOT' or operation == 'NOTS':
        return not a


def makeStr(list_of_chr):
    string = ''
    for x in list_of_chr:
        string += x
    return string


def getSymbType(arg):
    types = ['int', 'string', 'bool', 'nil', 'float']
    type = arg.type
    if type == 'var':
        return getType(arg.value)
    elif type in types:
        return type
    else:
        writeErr(53, 'Wrong type of operands')


def getSymb(arg, types=['int', 'string', 'bool', 'nil', 'float'], empty=False):
    if arg.type == 'var':
        val = getValue(arg.value)
        if empty and val is None:
            writeErr(56, 'Wrong value of operands')
        else:
            if getType(arg.value) in types:
                return val
            else:
                writeErr(53, 'Wrong type of operands')
    else:
        arg.value = checkConst(arg)
        if empty and arg.value is None:
            writeErr(56, 'Wrong value of operands')
        else:
            if arg.type in types:
                return arg.value
            else:
                writeErr(53, 'Wrong type of operands')


def checkLength(length, ref):
    if length != ref:
        writeErr(32, 'Wrong number of arguments')


def EOF(f):
    current_pos = f.tell()
    file_size = os.fstat(f.fileno()).st_size
    return current_pos >= file_size


g_frame = {}
i = 0
stack = Stack()
call_stack = Stack()
data_stack = Stack()
while int(i) < len(instruction):
    inst = instruction[i]
    if inst.name == 'DEFVAR':
        checkLength(len(inst.args), 1)
        if checkVarA(inst.args[0].value):
            writeErr(52, 'Trying to redefine variable')
        var = re.split('@', inst.args[0].value)
        if checkFrame('GF') and var[0] == 'GF':  # check whether the frame exists, but it should always exists
            g_frame[inst.args[0].value] = Variable(var[0], var[1])
        elif checkFrame('TF') and var[0] == 'TF':  # check whether the frame exists
            t_frame[inst.args[0].value] = Variable(var[0], var[1])
        elif checkFrame('LF') and var[0] == 'LF':  # check whether the frame exists
            l_frame[inst.args[0].value] = Variable(var[0], var[1])
    elif inst.name == 'MOVE':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        if inst.args[1].type == 'var':
            putValue(inst.args[0].value, getValue(inst.args[1].value), getType(inst.args[1].value))
        else:
            val = getSymb(inst.args[1])
            val_type = getSymbType(inst.args[1])
            putValue(inst.args[0].value, val, val_type)
    elif inst.name == 'CREATEFRAME':
        checkLength(len(inst.args), 0)
        t_frame = {}
        t_frame.clear()
    elif inst.name == 'PUSHFRAME':
        checkLength(len(inst.args), 0)
        try:
            tmp_l_frame = t_frame.copy()
            l_frame = {}
            for x, y in tmp_l_frame.items():
                var = re.split('@', x)
                l_frame['LF@' + str(var[1])] = tmp_l_frame[x]
            stack.push(l_frame)
            l_frame = stack.top()
            del tmp_l_frame
            del t_frame
        except:
            writeErr(55, 'Temporary frame is not defined')
    elif inst.name == 'POPFRAME':
        checkLength(len(inst.args), 0)
        if stack.isEmpty():
            writeErr(55, 'Frame stack is empty')
        else:
            t_frame = {}
            t_frame.clear()
            tmp_t_frame = stack.pop()
            for x, y in tmp_t_frame.items():
                var = re.split('@', x)
                t_frame['TF@' + str(var[1])] = tmp_t_frame[x]
            if stack.isEmpty():
                del l_frame
            else:
                l_frame.clear()
                l_frame = stack.top()
    elif inst.name == 'LABEL':
        pass
    elif inst.name == 'JUMP':
        try:
            i = int(labels[inst.args[0].value])
        except:
            writeErr(52, 'Label with this name does not exists')
    elif inst.name == 'EXIT':
        checkLength(len(inst.args), 1)
        if inst.args[0].type == 'int':
            checkConst(inst.args[0])
            if 0 <= int(inst.args[0].value) <= 49:
                exit(int(inst.args[0].value))
            else:
                writeErr(57, 'Wrong exit value')
        elif inst.args[0].type == 'var':
            if getType(inst.args[0].value) == 'int':
                if 0 <= int(getValue(inst.args[0].value)) <= 49:
                    exit(int(getValue(inst.args[0].value)))
                else:
                    writeErr(57, 'Wrong exit value')
            elif getType(inst.args[0].value) == 'var':
                writeErr(56, 'Wrong value of operands')
            else:
                writeErr(53, 'Wrong type of operands')
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'BREAK':
        checkLength(len(inst.args), 0)
        sys.stderr.write('Global frame : ')
        for x in g_frame:
            sys.stderr.write(x + ', ')
        sys.stderr.write('\nTemporary frame : ')
        try:
            for x in t_frame:
                sys.stderr.write(x)
        except:
            sys.stderr.write('is empty')
        sys.stderr.write('\nLocal frame : ')
        try:
            for x in l_frame:
                sys.stderr.write(x)
        except:
            sys.stderr.write('is empty')
        sys.stderr.write('\nCurrent instruction is ' + inst.name + ' and its order is ' + inst.order)
    elif inst.name == 'CALL':
        checkLength(len(inst.args), 1)
        call_stack.push(i)
        try:
            i = int(labels[inst.args[0].value])
        except:
            writeErr(52, 'Label with this name does not exists')
    elif inst.name == 'RETURN':
        checkLength(len(inst.args), 0)
        if call_stack.isEmpty():
            writeErr(56, 'CALL stack is empty')
        else:
            i = call_stack.pop()
    elif inst.name == 'WRITE':
        checkLength(len(inst.args), 1)
        print(getSymb(inst.args[0]), end='')
    elif inst.name == 'READ':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        if inst.args[1].type != 'type':
            writeErr(53, 'Wrong type of operand')
        input = input_file.readline().strip()
        if inst.args[1].value == 'string':
            if EOF(input_file) and input == '':
                putValue(inst.args[0].value, '', 'nil')
            else:
                putValue(inst.args[0].value, convertString(input), 'string')
        elif inst.args[1].value == 'bool':
            if input.lower() == 'true' or input.lower() == 'false':
                putValue(inst.args[0].value, input.lower(), inst.args[1].value)
            elif EOF(input_file) and input == '':
                putValue(inst.args[0].value, '', 'nil')
            else:
                putValue(inst.args[0].value, 'false', 'bool')
        elif inst.args[1].value == 'int':
            try:
                putValue(inst.args[0].value, int(input), inst.args[1].value)
            except:
                putValue(inst.args[0].value, '', 'nil')
        elif inst.args[1].value == 'float':
            input = getFloat(input)
            try:
                putValue(inst.args[0].value, input, inst.args[1].value)
            except:
                putValue(inst.args[0].value, '', 'nil')
        else:
            putValue(inst.args[0].value, input, inst.args[1].value)
    elif inst.name == 'DPRINT':
        checkLength(len(inst.args), 1)
        sys.stderr.write(str(getSymb(inst.args[0])))
    elif inst.name == 'ADD' or inst.name == 'SUB' or inst.name == 'MUL' or inst.name == 'IDIV' or inst.name == 'DIV' \
        or inst.name == 'ADDS' or inst.name == 'SUBS' or inst.name == 'MULS' or inst.name == 'IDIVS' or inst.name == 'DIVS':
        is_stack = False
        types = ['float', 'int']
        if len(inst.name) > 3 and inst.name != 'IDIV':  #short version of check whether it is stack operands
            b = data_stack.pop()
            b_type = data_stack.pop()
            a = data_stack.pop()
            a_type = data_stack.pop()
            if not a_type in types or not b_type in types :
                writeErr(53, 'Wrong type of operands')
            is_stack = True
            checkLength(len(inst.args), 0)
        else:
            a_type = getSymbType(inst.args[1])
            b_type = getSymbType(inst.args[2])
            a = getSymb(inst.args[1], ['int', 'float'])
            b = getSymb(inst.args[2], ['int', 'float'])
            checkLength(len(inst.args), 3)
            checkVar(inst.args[0].value)
        is_float = False
        if a_type == 'float' or b_type == 'float':
            is_float = True
        if a_type != b_type:
            writeErr(53, 'Wrong type of operands')
        if is_float:
            if is_stack:
                data_stack.push('float')
                data_stack.push(doMath(inst.name, a, b, True).hex())
            else:
                putValue(inst.args[0].value, doMath(inst.name, a, b, True).hex(), 'float')
        else:
            if is_stack:
                data_stack.push('int')
                data_stack.push(doMath(inst.name, a, b, False))
            else:
                putValue(inst.args[0].value, doMath(inst.name, a, b, False), 'int')
    elif inst.name == 'LT' or inst.name == 'GT' or inst.name == 'EQ' or inst.name == 'JUMPIFEQ' or inst.name == 'JUMPIFNEQ':
        checkLength(len(inst.args), 3)
        a = getSymb(inst.args[1], empty=True)
        b = getSymb(inst.args[2], empty=True)
        a_type = getSymbType(inst.args[1])
        b_type = getSymbType(inst.args[2])
        can_jump = False
        if inst.name == 'JUMPIFEQ' or inst.name == 'JUMPIFNEQ':
            if inst.args[0].value in labels:
                can_jump = True
            else:
                writeErr(52, 'Label with this name does not exists')
        else:
            checkVar(inst.args[0].value)
        if (a_type == 'nil' or b_type == 'nil') and (
                inst.name == 'EQ' or inst.name == 'JUMPIFEQ' or inst.name == 'JUMPIFNEQ'):
            if can_jump:
                if inst.name == 'JUMPIFEQ' and doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
                elif inst.name == 'JUMPIFNEQ' and not doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
            else:
                putValue(inst.args[0].value, str(a == b).lower(), 'bool')
        elif a_type == b_type and (a_type != 'nil' or b_type != 'nil'):
            if can_jump:
                if inst.name == 'JUMPIFEQ' and doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
                elif inst.name == 'JUMPIFNEQ' and not doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
            else:
                putValue(inst.args[0].value, str(doCompare(inst.name, a, b)).lower(), 'bool')
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'LTS' or inst.name == 'GTS' or inst.name == 'EQS':
        checkLength(len(inst.args), 0)
        b = data_stack.pop()
        b_type = data_stack.pop()
        a = data_stack.pop()
        a_type = data_stack.pop()
        if inst.name == 'EQS' and (a_type == 'nil' or b_type == 'nil'):
            data_stack.push('bool')
            data_stack.push(str(doCompare(inst.name, a, b)).lower())
        elif a_type == b_type:
            data_stack.push('bool')
            data_stack.push(str(doCompare(inst.name, a, b)).lower())
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'JUMPIFEQS' or inst.name == 'JUMPIFNEQS':
        checkLength(len(inst.args), 1)
        b = data_stack.pop()
        b_type = data_stack.pop()
        a = data_stack.pop()
        a_type = data_stack.pop()
        if inst.args[0].value in labels:
            if (inst.name == 'JUMPIFEQS' or inst.name == 'JUMPIFNEQS') and (a_type == 'nil' or b_type == 'nil'):
                if inst.name == 'JUMPIFEQS' and doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
                elif inst.name == 'JUMPIFNEQS' and not doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
            elif a_type == b_type:
                if inst.name == 'JUMPIFEQS' and doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
                elif inst.name == 'JUMPIFNEQS' and not doCompare('EQ', a, b):
                    i = int(labels[inst.args[0].value])
            else:
                writeErr(53, 'Wrong type of operands')
        else:
            writeErr(52, 'Label with this name does not exists')
    elif inst.name == 'AND' or inst.name == 'OR':
        checkLength(len(inst.args), 3)
        checkVar(inst.args[0].value)
        a = getSymb(inst.args[1], ['bool'])
        if a == 'true':
            a = True
        else:
            a = False
        b = getSymb(inst.args[2], ['bool'])
        if b == 'true':
            b = True
        else:
            b = False
        putValue(inst.args[0].value, str(doLogic(inst.name, a, b)).lower(), 'bool')
    elif inst.name == 'ANDS' or inst.name == 'ORS':
        checkLength(len(inst.args), 0)
        b = data_stack.pop()
        b_type = data_stack.pop()
        a = data_stack.pop()
        a_type = data_stack.pop()
        if a_type != 'bool' or b_type != 'bool':
            writeErr(53, 'Wrong type of operands')
        else:
            if a == 'true':
                a = True
            else:
                a = False
            if b == 'true':
                b = True
            else:
                b = False
        data_stack.push('bool')
        data_stack.push(str(doLogic(inst.name, a, b)).lower())
    elif inst.name == 'NOT':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        a = getSymb(inst.args[1], ['bool'])
        if a == 'true':
            a = True
        else:
            a = False
        putValue(inst.args[0].value, str(doLogic('NOT', a, a)).lower(), 'bool')
    elif inst.name == 'NOTS':
        checkLength(len(inst.args), 0)
        a = data_stack.pop()
        a_type = data_stack.pop()
        if a_type != 'bool':
            writeErr(53, 'Wrong type of operands')
        else:
            if a == 'true':
                a = True
            else:
                a = False
        data_stack.push('bool')
        data_stack.push(str(doLogic(inst.name, a, a)).lower())
    elif inst.name == 'PUSHS':
        checkLength(len(inst.args), 1)
        if inst.args[0].type == 'var':
            checkVar(inst.args[0].value)
            data_stack.push(getType(inst.args[0].value))
            data_stack.push(getValue(inst.args[0].value))
        else:
            data_stack.push(inst.args[0].type)
            if inst.args[0].type == 'string':
                data_stack.push(convertString(inst.args[0].value))
            else:
                data_stack.push(getSymb(inst.args[0]))
    elif inst.name == 'POPS':
        checkLength(len(inst.args), 1)
        checkVar(inst.args[0].value)
        if data_stack.isEmpty():
            writeErr(56, 'Stack is empty')
        value = data_stack.pop()
        type = data_stack.pop()
        putValue(inst.args[0].value, value, type)
    elif inst.name == 'INT2CHAR':  # symbol musi byt iba int
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        x = getSymb(inst.args[1], ['int'], True)
        if 0 <= x <= 999:
            putValue(inst.args[0].value, chr(x), 'string')
        else:
            writeErr(58, 'Wrong value of int')
    elif inst.name == 'INT2CHARS':
        checkLength(len(inst.args), 0)
        x = data_stack.pop()
        x_type = data_stack.pop()
        if x_type == 'int':
            if 0 <= x <= 999:
                data_stack.push('string')
                data_stack.push(chr(x))
            else:
                writeErr(58, 'Wrong value of int')
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'STRI2INT':
        checkLength(len(inst.args), 3)
        checkVar(inst.args[0].value)
        a = convertString(getSymb(inst.args[1], ['string']))
        b = int(getSymb(inst.args[2], ['int']))
        try:
            if b < 0:
                exit(99)
            putValue(inst.args[0].value, ord(a[b]), 'int')
        except:
            writeErr(58, 'Index is out of range')
    elif inst.name == 'STRI2INTS':
        checkLength(len(inst.args), 0)
        b = data_stack.pop()
        b_type = data_stack.pop()
        a = data_stack.pop()
        a_type = data_stack.pop()
        if b_type == 'int' and a_type == 'string':
            try:
                if b < 0:
                    exit(99)
                data_stack.push('int')
                data_stack.push(ord(a[b]))
            except:
                writeErr(58, 'Index is out of range')
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'CONCAT':
        checkLength(len(inst.args), 3)
        checkVar(inst.args[0].value)
        a = getSymb(inst.args[1], ['string'])
        b = getSymb(inst.args[2], ['string'])
        putValue(inst.args[0].value, a + b, 'string')
    elif inst.name == 'STRLEN':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        putValue(inst.args[0].value, len(getSymb(inst.args[1], ['string'])), 'int')
    elif inst.name == 'GETCHAR':
        checkLength(len(inst.args), 3)
        checkVar(inst.args[0].value)
        a = convertString(getSymb(inst.args[1], ['string']))
        b = int(getSymb(inst.args[2], ['int']))
        try:
            if b < 0:
                exit(99)
            putValue(inst.args[0].value, a[b], 'string')
        except:
            writeErr(58, 'Index is out of range')
    elif inst.name == 'SETCHAR':
        checkLength(len(inst.args), 3)
        x = getSymb(inst.args[0], ['string'])
        a = int(getSymb(inst.args[1], ['int']))
        b = convertString(getSymb(inst.args[2], ['string']))
        try:
            if a < 0:
                exit(99)
            x = list(x)
            x[a] = b[0]
            x = makeStr(x)
            putValue(inst.args[0].value, x, 'string')
        except:
            writeErr(58, 'Index is out of range')
    elif inst.name == 'TYPE':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        type = inst.args[1].type
        if inst.args[1].type == 'var':
            checkVar(inst.args[1].value)
            if getValueA(inst.args[1].value) is None:
                putValue(inst.args[0].value, '', 'string')
            else:
                putValue(inst.args[0].value, getType(inst.args[1].value), 'string')
        elif type == 'int' or type == 'string' or type == 'bool' or type == 'nil' or type == 'float':
            putValue(inst.args[0].value, inst.args[1].type, 'string')
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'INT2FLOAT':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        a = getSymb(inst.args[1], ['int'])
        putValue(inst.args[0].value, float(a).hex(), 'float')
    elif inst.name == 'INT2FLOATS':
        checkLength(len(inst.args), 0)
        a = data_stack.pop()
        a_type = data_stack.pop()
        if a_type == 'int':
            data_stack.push('float')
            data_stack.push(float(a).hex())
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'FLOAT2INT':
        checkLength(len(inst.args), 2)
        checkVar(inst.args[0].value)
        a = getSymb(inst.args[1], ['float'])
        putValue(inst.args[0].value, int(float.fromhex(a)), 'int')
    elif inst.name == 'FLOAT2INTS':
        checkLength(len(inst.args), 0)
        a = data_stack.pop()
        a_type = data_stack.pop()
        if a_type == 'float':
            data_stack.push('int')
            data_stack.push(int(float.fromhex(a)))
        else:
            writeErr(53, 'Wrong type of operands')
    elif inst.name == 'CLEARS':
        if not data_stack.isEmpty():
            data_stack.clear()
    else:
        writeErr(32, 'Wrong op code')
    i += 1

if args.input is not None:
    input_file.close()
