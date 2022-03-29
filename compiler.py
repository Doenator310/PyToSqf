import ast
from pprint import pprint
import sys
#######################
#
#  Copyright (C) 2019 David H. <Doenator/Doee>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################DEBUG################################
DEBUG = False
#########################VERSION#############################
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    raise Exception("Must be using Python 3.9 or newer!")
#########################GLOBALS#############################

OPERATORS = {ast.Add:"+", ast.Sub:"-", ast.Mult:"*", ast.Div:"/", ast.Mod:"%", ast.Not:"not"}
cmpOPERATORS = {ast.Eq:"==", ast.NotEq :"!=", ast.Lt :"<", ast.LtE  :"<=", ast.Gt :">", ast.GtE  :">=",
    ast.Is:"==",ast.In:"in", ast.IsNot:"!=", ast.NotIn:"not in", ast.Not:"not"}
boolOperators = {ast.And:"&&", ast.Or:"||"}

SQF_CONTEXT = {}

STATIC_FUNCTION_PREFIX = ["ENGINE","STATIC", "GLOBAL"]
STATIC_VAR_ACCESS = ["ENGINE","STATIC", "GLOBAL"]
RESERVED_NAMES=["player"]

FUNC_RET_NAME = "________ret"
JMP_RET_LABEL = "TORETURN______"

SPECIAL_FUNCTIONS = [{"name":"str", "new":"str", "call":False},
{"name":"float", "new":"toFixed", "call":False},
{"name":"int", "new":"parseNumber", "call":False},
{"name":"len", "new":"count", "call":False},
{"name":"print", "new":"hint", "call":False},
{"name":"pop", "new":"deleteAt", "call": False},
{"name":"isNil", "new":"isNil", "call": False},
{"name":"spawn", "new":"spawn", "call": False}]
##############################GLOBAL#FUNCS#####################################
def isNameInSpecialFunctions(name):
    for entry in SPECIAL_FUNCTIONS:
        if entry["name"] == name:
            return True
    return False

def getSpecialFunctionInfo(name):
    for entry in SPECIAL_FUNCTIONS:
        if entry["name"] == name:
            return entry
    return None

def isDefinedRegistered(ctx, var):
    if var in RESERVED_NAMES:
        return True
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
    if varName not in RESERVED_NAMES and  varName[0].isupper() == False:
        return "_" + varName
    return varName

def getOperatorSymbol(opType):
    if opType in OPERATORS:
        return OPERATORS[opType]
    raise Exception("Unknown Operator" + str(opType))

def getBoolOperatorSymbol(opType):
    if opType in boolOperators:
        return boolOperators[opType]
    raise Exception("Unknown Operator" + str(opType))
    pass

def getCMPOperatorSymbol(opType):
    if opType in cmpOPERATORS:
        return cmpOPERATORS[opType]
    raise Exception("Unknown Operator" + str(opType))

##################################SQF#SRC#NODE#########################################

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
        if parent != None and DEBUG:
            print(parent.ref, "<-|" ,self.ref, self.isExpression, type(self.ref).__bases__, self.hasCode)
        pass
#####################HELPER#FUNCTIONS###########################
    def getParentFunction(self):
        lastParent = self.parentNode
        while lastParent != None and lastParent.type != ast.FunctionDef:
            lastParent = lastParent.parentNode
        return lastParent

    def getParentByType(self, toSearch):
        lastParent = self.parentNode
        while lastParent != None and lastParent.type != toSearch:
            lastParent = lastParent.parentNode
        return lastParent

    def addChild(self, child):
        self.childNodes += [child]

    def getChildNodes(self):
        return self.childNodes

    def getChildByRef(self, refToSearch):
        for x in self.childNodes:
            if x.ref == refToSearch:
                return x
        return None

    def getChildNodesAfterNodeRef(self, refToSearch):
        nodes = []
        found = False
        for x in self.childNodes:
            if x.ref == refToSearch:
                found = True
            if found == True:
                nodes += [x]
        return nodes

    def getChildByType(self, typeToSearch):
        for x in self.childNodes:
            if x.type == typeToSearch:
                return x
        return None
#####################THE#HEAVY#OR#MAIN#PART##################################
    def toSyntax(self):
        preSpacing = " " * self.deepness * 3
        preSpacingDeeper = " " * (self.deepness +1) * 3
        fr = preSpacing
        m = ""
        end = preSpacing

        if self.hasCode:
            #anything but main!
            if self.isMain == False:
                if self.type == ast.FunctionDef:
                    fr += self.ref.name + " = "
                    fr +=  "{\n"
                    end += "\n};\n"
                    if len(self.ref.body) > 0:
                        bodyNode = self.getChildNodesAfterNodeRef(self.ref.body[0])
                        for node in bodyNode:
                            m += node.toSyntax()

                if self.type == ast.While:
                    fr += "while {" + self.getChildByRef(self.ref.test).toSyntax() + "} do {\n"
                    m = ""
                    if len(self.ref.body) > 0:
                        bodyNode = self.getChildNodesAfterNodeRef(self.ref.body[0])
                        for node in bodyNode:
                            m += node.toSyntax()
                    end += "};\n"
                elif self.type == ast.If:
                    fr += "if (" + self.getChildByRef(self.ref.test).toSyntax() + ") then {\n"
                    #build nodes D:
                    m = ""
                    if len(self.ref.body) > 0:
                        for nodeRef in self.ref.body:
                            node = self.getChildByRef(nodeRef)
                            m += node.toSyntax()
                    hasElse = len(self.ref.orelse) > 0
                    if hasElse:
                        end = preSpacing + "}"
                    else:
                        end = preSpacing + "};\n"
                    if hasElse == True:
                        end += " else {\n"
                        if(type(self.ref.orelse[0]) == ast.If):
                            end += self.getChildByRef(self.ref.orelse[0]).toSyntax()
                        else:
                            for nodeRef in self.ref.orelse:
                                node = self.getChildByRef(nodeRef)
                                end += node.toSyntax()
                        end += preSpacing +"};\n"
                elif self.type == ast.For:
                    forEachLoop = True
                    iterSyntax = self.getChildByRef(self.ref.iter).toSyntax();
                    if "range" in iterSyntax:
                        forEachLoop = False
                    if forEachLoop:
                        fr += "{\n"
                        iterName = self.getChildByRef(self.ref.target).toSyntax()
                        if iterName != "_x":
                            if "private" not in iterName:
                                iterName = "private " + iterName
                            m += preSpacingDeeper  + iterName + " = _x;\n"
                        #build body!
                        if len(self.ref.body) > 0:
                            bodyNode = self.getChildNodesAfterNodeRef(self.ref.body[0])
                            for node in bodyNode:
                                m += node.toSyntax()

                        end += "} forEach " + iterSyntax + ";\n"
                    else:
                        iterName = self.getChildByRef(self.ref.target).toSyntax()
                        #quick hack weil keine zeit..
                        iterNameCleaned = self.getChildByRef(self.ref.target).toSyntax()
                        if "private" not in iterName:
                            fr += "for[{" + "private " +iterName
                        else:
                            fr += "for[{" + iterNameCleaned
                        iterNode = self.getChildByRef(self.ref.iter)
                        upperLimit = iterNode.ref.args[-1].value
                        lowerLimit = iterNode.ref.args[0].value
                        if len(iterNode.ref.args) != 2:
                            lowerLimit = 0

                        fr += " = "+str(lowerLimit)+"},{" + iterNameCleaned + "<" + str(upperLimit) + \
                            "},{" + iterNameCleaned + " = " + iterNameCleaned + " + 1}]"
                        fr += " do {\n"
                        if len(self.ref.body) > 0:
                            bodyNode = self.getChildNodesAfterNodeRef(self.ref.body[0])
                            for node in bodyNode:
                                m += node.toSyntax()
                        end += "};\n"


            #if none of the above
            else:# if main then start with the file self!
                for child in self.childNodes:
                    m += child.toSyntax()
#/////////////////////////////////////////
        elif self.type == ast.Expr:
            for child in self.childNodes:
                m += child.toSyntax()
            end = ";\n"

            m = m.strip()
            end.strip()
#/////////////////////////////////////////
        elif self.type in [ast.Assign, ast.AugAssign, ast.AugAssign]:
            nameNode = self.getChildByType(ast.Name)
            targetElement = None
            if hasattr(self.ref, "targets"):
                targetElement = self.ref.targets[0]
            if hasattr(self.ref, "target"):
                targetElement = self.ref.target

            targetElementSqfNode = self.getChildByRef(targetElement)
            isAttributAssignment = targetElementSqfNode.type == ast.Attribute
            if hasattr(targetElement, "id") == True or isAttributAssignment:
                varName = ""
                isAlreadyDefined = False
                if isAttributAssignment:
                    varName = targetElementSqfNode.toSyntax()
                    isAlreadyDefined = True
                else:
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
                if self.type == ast.AugAssign:
                    m += varName
                    opType = type(self.ref.op)
                    if opType == ast.Add:
                        m += " + "
                    if opType == ast.Sub:
                        m += " - "
                    if opType == ast.Mult:
                        m += " * "
                    if opType == ast.Div:
                        m += " / "
                valueNode = self.getChildByRef(self.ref.value)
                end = valueNode.toSyntax()
                end += ";\n"
            else:
                #IF NOT JUST A VAR! For example, its a list!
                fr = self.getChildByRef(targetElement).toSyntax()
                m = " ("
                valueNode = self.getChildByRef(self.ref.value)
                end = valueNode.toSyntax().strip()
                end += ")];\n"
#/////////////////////////////////////////
        elif self.type == ast.UnaryOp:
            operator = getOperatorSymbol(type(self.ref.op))
            content = self.getChildByRef(self.ref.operand)
            fr = operator
            m = "("+ content.toSyntax() + ")"
            end = ""
#/////////////////////////////////////////
        elif self.type == ast.Call:
            funcObj = self.getChildByRef(self.ref.func)
            isAttributeFunc = isinstance(funcObj.ref, ast.Attribute)
            #check if special func like str()
            isSpecialFunction = False
            wasSpecialAttributeBefore = isAttributeFunc
            if isAttributeFunc == False:
                specialFunctionData = getSpecialFunctionInfo(funcObj.ref.id)
                isSpecialFunction = specialFunctionData is not None
            else:
                specialFunctionData = getSpecialFunctionInfo(funcObj.ref.attr)
                isSpecialFunction = specialFunctionData is not None

            if isSpecialFunction:
                isAttributeFunc = (specialFunctionData["call"] == False)
            #handle call
            if isAttributeFunc == False:
                fr  = ""
                if len(self.ref.args) > 0:
                    if len(self.ref.args) > 1:
                        fr += " ["
                    for refChild in self.ref.args:
                        childNodeArg = self.getChildByRef(refChild)
                        fr += childNodeArg.toSyntax()
                        if refChild != self.ref.args[-1]:
                            fr += ","
                    if len(self.ref.args) > 1:
                        fr += "] "
                m   = " call "
                # this is valid because function calls never have other names ^^
                end = funcObj.ref.id + ""
            else:
                fr  = ""
                objNameRef = None
                attrName   = None
                if isSpecialFunction == False or wasSpecialAttributeBefore:
                    attrName = funcObj.ref.attr
                    #check for replacement name
                    if isSpecialFunction == True:
                        attrName = specialFunctionData['new']

                    objNameRef = funcObj.getChildByRef(funcObj.ref.value)
                    if objNameRef is None:
                        node = funcObj.ref.value
                        objNameRef = SQFNode(node, type(node), funcObj.ref, funcObj, funcObj.iterDeepness + 1)
                    if objNameRef.ref.id not in STATIC_FUNCTION_PREFIX:
                        m = (objNameRef.toSyntax().strip() + " " + attrName).strip()
                    else:
                        m = (attrName).strip()

                else:
                    m = specialFunctionData['new']

                #Build argument list
                #fr = "(" + self.getChildByRef(funcObj.ref.value).toSyntax() + " "
                end = ""
                arg = ""
                specialArgs = False
                #CHECK IF SPAWN WAS USED!
                if specialFunctionData != None:
                    if specialFunctionData["name"] == "spawn":
                        specialArgs = True
                        arg = "["
                        for refChild in self.ref.args[1:]:
                            childNodeArg = self.getChildByRef(refChild)
                            arg += childNodeArg.toSyntax()
                            if refChild != self.ref.args[-1]:
                                arg += ","

                        arg += "] "
                        fr = arg + " " + fr
                        end += "("+ self.getChildByRef(self.ref.args[0]).toSyntax() + ")"
                #NORMAL CALL!
                if not specialArgs:

                    if len(self.ref.args) > 1:
                        arg = "["
                    elif len(self.ref.args) == 1:
                        arg = "("

                    for refChild in self.ref.args:
                        childNodeArg = self.getChildByRef(refChild)
                        arg += childNodeArg.toSyntax()
                        if refChild != self.ref.args[-1]:
                            arg += ","

                    if len(self.ref.args) > 1:
                        arg += "] "
                    elif len(self.ref.args) == 1:
                        arg += ")"
                    end += arg
#/////////////////////////////////////////
        elif self.type == ast.arguments:
            #if self.parentNode.type:
            fr += "params ["
            end = "];\n"
            for child in self.childNodes:
                m += child.toSyntax()
                if child != self.childNodes[-1]:
                    m += ","
#/////////////////////////////////////////
        elif self.type == ast.arg:
            fr, m, end = "\"", "", "\""
            varName = correctVarName(self.ref.arg)
            #register as local func params :D
            func = self.getParentFunction()
            addToRegistered(func, varName)
            m = varName # private is not needed here :)
#/////////////////////////////////////////
        elif self.type == ast.Constant:
            fr, m, end = "","",""
            if(str == type(self.ref.value)):
                m = "\"" +self.ref.value + "\""
            elif bool == type(self.ref.value):
                m = str(self.ref.value).lower()
            else:
                m = str(self.ref.value)
#/////////////////////////////////////////
        elif self.type == ast.BinOp:
            left = self.getChildByRef(self.ref.left)
            right = self.getChildByRef(self.ref.right)
            operator = self.getChildByRef(self.ref.op)
            fr = "("+ left.toSyntax()
            m = " " + operator.toSyntax() + " "
            end = right.toSyntax() + ")"

#/////////////////////////////////////////
        elif ast.operator in type(self.ref).__bases__:
            fr  = ""
            end =""
            m = getOperatorSymbol(self.type)
#/////////////////////////////////////////
        elif self.type == ast.Name:
            varName = correctVarName(self.ref.id)
            #Muss noch untersucht werden, macht das hier probleme ohne definitionsüberwachung?
            fr, m, end = "", varName, ""
#/////////////////////////////////////////
        elif self.type == ast.List:
            fr, end = "[", "]"
            for refChild in self.ref.elts:
                childNodeArg = self.getChildByRef(refChild)
                fr += childNodeArg.toSyntax()
                if refChild != self.ref.elts[-1]:
                    fr += ","
#/////////////////////////////////////////
        elif self.type == ast.Subscript:
            childNodeArg = self.getChildByRef(self.ref.slice)
            #check if parent is left side assign!
            isAssignment = False
            #list is assigned
            assignInParent = self.getParentByType(ast.Assign)
            if assignInParent != None:
                isAssignment = (self.ref in assignInParent.ref.targets)
            #assignment check ended!
            fr  = self.getChildByRef(self.ref.value).toSyntax()
            if isAssignment == False:
                #this builds "(arr select index)"
                fr = "(" + fr
                m   = " select " + childNodeArg.toSyntax() + ""
                end = ")"
            else:
                # this function builds the "[index,"  of  <"arr set [index, value]">
                fr = fr + " set ["
                m = childNodeArg.toSyntax()
                end = ","
#/////////////////////////////////////////
        elif self.type == ast.Attribute:
            prefix = self.getChildByRef(self.ref.value).toSyntax()
            fr = ""
            end = ""
            if prefix in STATIC_VAR_ACCESS:
                m = self.ref.attr
            else:
                raise Exception("Failed attribut access because not implemented yet")
            pass
#/////////////////////////////////////////
        elif self.type == ast.Pass:
            fr = ""
            m = ""
            end="\n"
#/////////////////////////////////////////
        elif self.type == ast.Compare:
            fr, m, end = "","",""
            fr = self.getChildByRef(self.ref.left).toSyntax() + " "
            if len(self.ref.ops) > 1:
                raise Exception("Not Supported!!!")
            m = getCMPOperatorSymbol(type(self.ref.ops[0]))
            end = " " + self.getChildByRef(self.ref.comparators[0]).toSyntax()
#/////////////////////////////////////////
        elif self.type == ast.BoolOp:
            leftCond = self.getChildByRef(self.ref.values[0])
            rightCond = self.getChildByRef(self.ref.values[1])
            symbol = getBoolOperatorSymbol(type(self.ref.op))
            fr = "("+ leftCond.toSyntax() + ")"
            m = symbol
            end = "("+ rightCond.toSyntax() + ")"
            pass
#/////////////////////////////////////////
        elif self.type == ast.Return:
            fr  += "if (true) exitWith {" + self.getChildByRef(self.ref.value).toSyntax() + "};\n";
            pass
#/////////////////////////////////////////
        elif self.type == ast.Await:
            if self.parentNode.hasCode == False and self.parentNode.type != ast.Expr:
                raise Exception("Invalid placement of await! did you forget to use '()'")
            fr += "waitUntil {"
            m += self.getChildByRef(self.ref.value).toSyntax()
            end = "}"
#/////////////////////////////////////////
        elif self.type == ast.Break:
            m,end = "break;","\n"
#/////////////////////////////////////////
        elif self.type == ast.Continue:
            m,end = "continue;","\n"
#/////////////////////////////////////////
        else:
            fr, m, end = "","",""
            print("MISSED ", self.type)
#/////////////////////////////////////////
        return fr + m + end

##################################NODE#CREATOR#########################################
sqfTree = None

knownNodes = []

def recursiveIterator(node, parentNode = None, sqfParent=None, iterDeepness = -1):
    newNode = SQFNode(node, type(node), parentNode, sqfParent, iterDeepness)
    for x in ast.iter_child_nodes(node):
        newNode.addChild(recursiveIterator(x, node, newNode, iterDeepness + 1))
    return newNode
##################################INTIIATOR#########################################
def convertPython3ToSQF(readFile):
    ast_tree = None
    with open(readFile, "r") as source:
        ast_tree = source.read()
    ast_tree = ast.parse(ast_tree)
    parent = None

    global sqfResult
    sqfNodeTree = recursiveIterator(ast_tree)
    sqfSyntax = sqfNodeTree.toSyntax()
    return sqfSyntax
##################################MAIN##############################################
import os
if __name__ == "__main__":
    if len (sys.argv) != 3:
        print("Usage: compiler.py fileIn.py fileOut.sqf")
    else:
        fileIn  = sys.argv[1]
        fileOut = sys.argv[2]
        print()
        print(f"[i] DebugMode = {DEBUG}")
        print(f"[i] Converting {os.path.basename(fileIn)} -> to {os.path.basename(fileOut)}!" )
        sqfSource = convertPython3ToSQF(fileIn)
        if DEBUG:
            with open("sqfResult.tmp.sqf","w") as f:
                f.write(sqfSource)
        with open(fileOut,"w") as f:
            f.write(sqfSource)
        print("[i] Finished")
        print("#######################################")
        print("################Success################")
        print("#######################################")
