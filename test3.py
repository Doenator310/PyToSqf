import ast
from pprint import pprint

sqfResult = ""
OPERATORS = {ast.Add:"+", ast.Sub:"-", ast.Mult:"*", ast.Div:"/", ast.Mod:"%"}
SQF_CONTEXT = {}


def isDefinedRegistered(ctx, var):
    if ctx not in SQF_CONTEXT:
        return False
    return var in SQF_CONTEXT[ctx]

def addToRegistered(ctx, var):
    oldDefines = []
    if ctx in SQF_CONTEXT:
        oldDefines = SQF_CONTEXT[ctx]
    updatedDefines = oldDefines + [var]
    SQF_CONTEXT[ctx] = updatedDefines

def correctVarName(varName):
    return "_" + varName

def getOperatorSymbol(opType):
    if opType in OPERATORS:
        return OPERATORS[opType]

    raise Exception("Unknown Operator" + str(opType))

class SQFNode:
    def __init__(self, ref, newType=None, refParent=None, parent=None,  deepness = 0):
        self.deepness = deepness
        self.type = newType
        self.parentNode = parent
        self.refParent = refParent
        self.childNodes = []
        self.ref = ref;
        self.ctx = None
        if hasattr(self.ref, "ctx"):
            self.ctx = self.ref.ctx
        self.isExpression = isinstance(ref, ast.expr)
        self.isMain  = isinstance(ref, ast.mod)
        self.hasCode = hasattr(self.ref, "body")
        if parent != None:
            print(parent.ref, "<-|" ,self.ref, self.isExpression, type(self.ref).__bases__, self.hasCode)
        pass

    def getParentFunction(self):
        lastParent = self.parentNode
        while lastParent != None and lastParent.type != ast.FunctionDef:
            lastParent = lastParent.parentNode
        return lastParent

    def addChild(self, child):
        self.childNodes += [child]

    def getChildNodes(self, child):
        return self.childNodes()

    def getChildByRef(self, refToSearch):
        for x in self.childNodes:
            if x.ref == refToSearch:
                return x
        return None

    def getChildByType(self, typeToSearch):
        for x in self.childNodes:
            if x.type == typeToSearch:
                return x
        return None

    def toSyntax(self):
        preSpacing = " " * self.deepness
        fr = preSpacing
        m = ""
        end = preSpacing

        if self.hasCode:
            if self.isMain == False:
                fr += self.ref.name + " = {\n"
                end += "};\n"
            for child in self.childNodes:
                m += child.toSyntax()

        elif self.type == ast.Expr:
            for child in self.childNodes:
                m += child.toSyntax()
            end = ";\n"

        elif self.type == ast.Assign:
            nameNode = self.getChildByType(ast.Name)
            varName = correctVarName(nameNode.ref.id)
            isAlreadyDefined = isDefinedRegistered(nameNode.ctx, varName)

            func = self.getParentFunction()
            isAlreadyDefinedInParentFunction = isDefinedRegistered(func, varName) and func != None

            if isAlreadyDefinedInParentFunction == False and isAlreadyDefined == False:
                addToRegistered(nameNode.ctx, varName)
                fr += "private " + varName
            else:
                fr += varName

            m = " = "
            valueNode = self.getChildByType(type(self.ref.value))
            end = valueNode.toSyntax()
            end += ";\n"
        elif self.type == ast.Call:
            fr  = "("
            if len(self.ref.args) > 0:
                fr += "["
                for refChild in self.ref.args:
                    childNodeArg = self.getChildByRef(refChild)
                    fr += childNodeArg.toSyntax()
                    if refChild != self.ref.args[-1]:
                        fr += ","
                fr += "] "

            funcName = self.getChildByRef(self.ref.func)
            m   = "call "
            # this is valid because function calls never have other names ^^
            end = funcName.ref.id + ")"


        elif self.type == ast.arguments:
            fr += "params ["
            end = "];\n"
            for child in self.childNodes:
                m += child.toSyntax()
                if child != self.childNodes[-1]:
                    m += ","

        elif self.type == ast.arg:
            fr, m, end = "\"", "", "\""
            varName = correctVarName(self.ref.arg)
            #register as local func params :D
            func = self.getParentFunction()
            addToRegistered(func, varName)
            m = varName # private is not needed here :)

        elif self.type == ast.Constant:
            fr, m, end = "","",""
            if(str == type(self.ref.value)):
                m = "\"" +self.ref.value + "\""
            else:
                m = str(self.ref.value)
        elif self.type == ast.BinOp:
            left = self.getChildByRef(self.ref.left)
            right = self.getChildByRef(self.ref.right)
            operator = self.getChildByRef(self.ref.op)
            fr = "("+ left.toSyntax()
            m = " " + operator.toSyntax() + " "
            end = right.toSyntax() + ")"

        elif ast.operator in type(self.ref).__bases__:
            fr = ""
            end =""
            m = getOperatorSymbol(self.type)
        elif self.type == ast.Name:
            varName = correctVarName(self.ref.id)
            #Muss noch untersucht werden, macht das hier probleme ohne definitionsüberwachung?
            fr, m, end = "", varName, ""
        elif self.type == ast.List:
            fr, end = "[", "]"
            for refChild in self.ref.elts:
                childNodeArg = self.getChildByRef(refChild)
                fr += childNodeArg.toSyntax()
                if refChild != self.ref.elts[-1]:
                    fr += ","
            pass
        else:
            fr, m, end = "","",""
            print("MISSED ", self.type)

        return fr + m + end

sqfTree = None

knownNodes = []


def recursiveIterator(node, parentNode = None, sqfParent=None, iterDeepness = -1):
    newNode = SQFNode(node, type(node), parentNode, sqfParent, iterDeepness)
    for x in ast.iter_child_nodes(node):
        newNode.addChild(recursiveIterator(x, node, newNode, iterDeepness + 1))
    return newNode

def main():
    print("YAS")
    ast_tree = None
    with open("sample.sqf.py", "r") as source:
        ast_tree = source.read()
    ast_tree = ast.parse(ast_tree)
    parent = None

    global sqfResult
    sqfNodeTree = recursiveIterator(ast_tree)
    print(sqfNodeTree.toSyntax())

if __name__ == "__main__":
    main()
    with open("sqfResult","w") as f:
        f.write(sqfResult)
