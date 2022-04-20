import sys


def writeErr(code, message=''):
    sys.stderr.write(message + '\n')
    exit(code)


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.insert(0, item)

    def pop(self):
        return self.items.pop(0)

    def top(self):
        return self.items[0]

    def printStack(self):
        print(self.items)

    def clear(self):
        self.items.clear()


class Argument:
    def __init__(self, arg_type, arg_value, arg_order):
        self.type = arg_type
        self.value = arg_value
        self.arg_order = arg_order


class Instruction:
    def __init__(self, name, order):
        self.name = name
        self.order = order
        self.my_order = 0
        self.args = []

    def addArgument(self, arg_type, arg_value, arg_order):
        self.args.append(Argument(arg_type, arg_value, arg_order))

    def checkOrdOfArgs(self):
        if len(self.args) != 0:
            if self.args[0].arg_order != 'arg1':
                writeErr(32, 'Wrong format of element')
        if len(self.args) != 1:
            for x in range(1, len(self.args)):
                if self.args[x].arg_order == self.args[x - 1].arg_order:
                    writeErr(32, 'Wrong format of element')
                if self.args[x].arg_order != 'arg' + str(x + 1):
                    writeErr(32, 'Wrong format of element')


class Variable:
    def __init__(self, frame, name):
        self.value = None
        self.type = 'var'
        self.frame = frame
        self.name = name

    def updateVar(self):
        if self.type == 'var' and self.value is not None:
            if self.type == 'nil':
                self.value = ''
            elif self.value == 'true' or self.value == 'false':
                self.type = 'bool'
                self.value = self.value
            elif self.checkInt():
                self.type = 'int'
                self.value = int(self.value)
            elif self.type == 'string' and self.value is None:
                self.value = ''
            else:
                self.type = 'string'

    def checkInt(self):
        try:
            int(self.value)
            return True
        except ValueError:
            return False
