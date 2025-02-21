#!/usr/bin/python3

##################### Watermelon++ source
#
####### Made by Aceinet 2022-present
# 
# Github: https://github.com/Aceinet
####################################

def crypt_string(string: str) -> str:
    x = ""
    for char in string:
        x += chr(ord(char)+4)
    x = x[::-1]+"\0"
    return x

def decrypt_string(string: str) -> str:
    x = string[:-1][::-1]
    result = ""
    for char in x:
        if char != "\x00": result += chr(ord(char)-4)

    return result

import os, sys, re, shlex, traceback, _thread, time, ctypes, dearpygui
import dearpygui.dearpygui as dpg
from ctypes import wintypes
import io
from contextlib import redirect_stdout
os.name = 123
if os.name == "nt":
    import ahk

variables = {
    "!hello": "Hello, world!",
    "WPPinput_nonblocking": 0
}

functions = {}


ifst = [{ # Information for current IF Statement in file
    "var": None,
    "equal": None,
    "active": False,
    "elsecon": False
}]

namespace_info = {
    "active": False,
    "name": ""
}

ifst = []

loopst = []

line_stamps = [] # Line stamps for functions

toexit = 0
class error: # Error thrower
    def throw(name, details):
        global inter, toexit
        print(f"""
__Execution error__
{name}: {details}""")
        toexit = 1
        if inter == 0: 
            exit(-5)
            toexit = 0


class warn: # Warning thrower
    def throw(name, details):
        print(f"""
Warning:
{name}: {details}""")
        
#############
#WPP: Scope
#############
class Scope:
    def __init__(self, scope={}):
        self.scope = scope
        self.timed_vars = []

scopes = {
    "global": Scope(variables.copy()),
    "essential": Scope()
}

current_scope = "global"
pyexec_allowed = True

##############
#WPP: TimedVar
##############
class TimedVar:
    def __init__(self, varname, lifetime_number, lifetime_number2,  last_type):
        self.varname = varname
        self.lifetime_number = lifetime_number
        self.lifetime_number2 = lifetime_number2
        self.last_type = last_type

##############
#WPP: Lexer
##############
class lexer:
    def __init__(self):
        pass

    def tokenize(self, code):
        self.code = code.replace(';', ' ;').replace('X[E0', ';') # Replacing like: out "hi"; to out "hi" ; for making word
        self.code = self.code.replace("\n", "\x01\n")
        src = shlex.split(self.code, posix=False) # Using shlex split for strings
        tokens = []

        for _word in src: # Looping through list items
            word = _word
            newline = False
            if _word[-1] == "\x01":
                newline = True
                word = "".join(list(word)[:-1])
            
            if len(word) == 0:
                word = "\x00"

            if word in ("println", "print"): tokens.append(["KOut", word])
            elif word == "scanln": tokens.append(["KInput", word])
            elif word == "var": tokens.append(["KVal", word])
            elif word == "return": tokens.append(["KReturn", word])
            elif word == "cast": tokens.append(["KConvert", word])
            elif word == "free": tokens.append(["KFree", word])
            #elif word == "include": tokens.append(["KInclude", word])
            elif word == "fn": tokens.append(["KFn", word])
            elif word == "len": tokens.append(["KLen", word])
            elif word == "getchar": tokens.append(["KGetChar", word])
            elif word == "__pyexec": tokens.append(["KPydef", word])
            elif word == "__deny_pyexec": tokens.append(["KPydefDeny", word])
            elif word == "__allow_pyexec": tokens.append(["KPydefAllow", word])
            elif word == "setchar": tokens.append(["KSetChar", word])
            elif word == "nf": tokens.append(["KIndentEnd", word])
            elif word == "call": tokens.append(["KFnCall", word])
            elif word == "namespace": tokens.append(["KNamespace", word])
            elif word == "nsEnd": tokens.append(["KNamespaceEnd", word])
            elif word == "exit": tokens.append(["KExit", word])
            elif word == "loop": tokens.append(["KLoop", word])
            elif word == "break": tokens.append(["KBreak", word])
            elif word == "lend": tokens.append(["KEndLoop", word])
            elif word == "sleep": tokens.append(["KSleep", word])
            elif word == "utime": tokens.append(["KUTime", word])
            elif word == "cp": tokens.append(["KCopy", word])
            #elif word == "goto": tokens.append(["KGoto", word])
            elif word == "?": tokens.append(["Comment", word])
            elif word == "-?": tokens.append(["CommentEnd", word])
            elif word == "none": tokens.append(["TNone", word])
            elif word in ("true", "false"): tokens.append(["TBool", word])
            elif word[0] == '"' and word[len(word)-1] == '"': tokens.append(["TStr", word[1:len(word)-1]])
            elif word == "if": tokens.append(["STif", word])
            elif word == "else": tokens.append(["STelse", word])
            elif word == "end": tokens.append(["STend", word])
            elif re.match("[a-z]", word) or re.match("[A-Z]", word): tokens.append(["Indentifier", word])
            elif word == ';': tokens.append(["End", word])
            elif word in "+-=/*": tokens.append(["Op", word])
            elif word == "==": tokens.append(["Eq", word])
            elif word == "!=": tokens.append(["NEq", word])
            elif word == ">": tokens.append(["More", word])
            elif word == "<": tokens.append(["Less", word])
            elif word == ">=": tokens.append(["MoreEq", word])
            elif word == "<=": tokens.append(["LessEq", word])
            else: 
                try:
                    if type(eval(word)) == int:  tokens.append(["TInt", word]) # Checking if word if float / int
                    elif type(eval(word)) == float:  tokens.append(["TFloat", word])
                    passed = True
                except SyntaxError:
                    tokens.append(["Indentifier", word])
            
            if tokens[-1][1] == "\x00":
                tokens.pop()

            if newline:
                tokens.append(["NEWLINE", "\x01"])

        tokens.append(["FLEnd", None]) # Adding empty token to prevent IndexError

        i = 0
        while i < len(tokens):
            if tokens[i][0] == "TStr":
                tokens[i][1] = tokens[i][1].replace("\x01", "")
            i += 1

        if verbose == True:
            print("Execution")
            print("Tokens:")
            print(tokens)
            print("-------\n\n")

        return tokens


###############
#WPP: Parser
###############
class parser:
    def __init__(self): pass

    def run(self, tokens):
        global toexit, lxr, prs, variables, functions, current_scope, pyexec_allowed
        self.tokens = tokens
        c = 0
        end = False
        iscomment = False
        function_definition = False
        skip_until_loop_end = False
        #for tkn in self.tokens:
        while c < len(tokens):

            for i in range(1, 10+1):
                if scopes["essential"].scope.get(f"arg{i}") == None: scopes["essential"].scope[f"arg{i}"] = 0
            if scopes["essential"].scope.get("ret") == None: scopes["essential"].scope["ret"] = 0

            variables = scopes[current_scope].scope.copy()
            if current_scope != "global":
                for variable in scopes["global"].scope:
                    variables[variable] = scopes["global"].scope[variable]
            for variable in scopes["essential"].scope:
                variables[variable] = scopes["essential"].scope[variable]
            prev_scope = current_scope


            if self.tokens[c][0] == "CommentEnd": iscomment = False

            if iscomment == True: 
                c += 1
                continue
                pass

            if tokens[c][0] != "KEndLoop":
                if skip_until_loop_end == True:
                    c += 1
                    continue
                    pass
            else:
                if skip_until_loop_end == True:
                    skip_until_loop_end = False

            if tokens[c][0] != "End":
                if verbose:
                    print(self.tokens[c][0], self.tokens[c][1])
        
            if toexit == 1: break

            if self.tokens[c][0] == "End": end = False 
            elif self.tokens[c][0] == "STend": 
                if len(ifst) > 0:
                    ifst.pop(-1)
            elif self.tokens[c][0] == "STelse":     
                if len(ifst) > 0:
                    ifst[-1]["elsecon"] = True

            if self.tokens[c][0] == "KIndentEnd": function_definition = False

            
            if end == True: 
                c += 1
                continue
            if function_definition == True:
                c += 1
                continue

            #print(ifst)
            if len(ifst) > 0:
                #print(f"active: {ifst}")
                if ifst[-1]["active"] == True: # Checking for 'IF' Statement is active
                    if ifst[-1]["elsecon"] == True: # If in statement found 'ELSE' block
                        if False:#ifst[-1]["equal"] in variables: # if second op is variable
                            if ifst[-1]["condition"] == "Eq":
                                if variables[ifst[-1]["var"]] == variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if variables[ifst[-1]["var"]] != variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if variables[ifst[-1]["var"]] > variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if variables[ifst[-1]["var"]] < variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if variables[ifst[-1]["var"]] >= variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if variables[ifst[-1]["var"]] <= variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                        else: # if second op is not variable
                            if ifst[-1]["condition"] == "Eq":
                                if ifst[-1]["var"] == ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if ifst[-1]["var"] != ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if ifst[-1]["var"] < ifst[-1]["equal"]:
                                    pass
                                else: c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if ifst[-1]["var"] > ifst[-1]["equal"]:
                                    pass
                                else: c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if ifst[-1]["var"] >= ifst[-1]["equal"]:
                                    pass
                                else: c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if ifst[-1]["var"] <= ifst[-1]["equal"]:
                                    pass
                                else: c += 1; continue
                            '''
                            if ifst[-1]["condition"] == "Eq":
                                if variables[ifst[-1]["var"]] == ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if variables[ifst[-1]["var"]] != ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if variables[ifst[-1]["var"]] > ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if variables[ifst[-1]["var"]] < ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if variables[ifst[-1]["var"]] >= ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if variables[ifst[-1]["var"]] <= ifst[-1]["equal"]:
                                    c += 1; continue'''
                
                    else: # if not else
                        if False:#ifst[-1]["equal"] in variables: # if second op is variable
                            if ifst[-1]["condition"] == "Eq":
                                if variables[ifst[-1]["var"]] != variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if variables[ifst[-1]["var"]] == variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if variables[ifst[-1]["var"]] < variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if variables[ifst[-1]["var"]] > variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if variables[ifst[-1]["var"]] <= variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if variables[ifst[-1]["var"]] >= variables[ifst[-1]["equal"]]:
                                    c += 1; continue
                        else: # if second op is not variable
                            
                            if ifst[-1]["condition"] == "Eq":
                                if ifst[-1]["var"] != ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if ifst[-1]["var"] == ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if ifst[-1]["var"] < ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if ifst[-1]["var"] > ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if ifst[-1]["var"] <= ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if ifst[-1]["var"] >= ifst[-1]["equal"]:
                                    c += 1; continue
                            '''
                            if ifst[-1]["condition"] == "Eq":
                                if variables[ifst[-1]["var"]] != ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "NEq":
                                if variables[ifst[-1]["var"]] == ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "More":
                                if variables[ifst[-1]["var"]] < ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "Less":
                                if variables[ifst[-1]["var"]] > ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "MoreEq":
                                if variables[ifst[-1]["var"]] <= ifst[-1]["equal"]:
                                    c += 1; continue
                            elif ifst[-1]["condition"] == "LessEq":
                                if variables[ifst[-1]["var"]] >= ifst[-1]["equal"]:
                                    c += 1; continue'''

            #print(tokens[c])
        
            if self.tokens[c][0] == "KOut": # Handler for 'out' keyword
                if self.tokens[c+1][0] not in ("TStr", "Indentifier"): 
                    error.throw("Out.TypeError", "Only strings accepted"); continue

                s = str(self.tokens[c+1][1])
                if self.tokens[c+1][0] == "Indentifier":
                    s = str(variables[self.tokens[c+1][1]])
                
                if self.tokens[c][1] == "println":
                    s += "\n"
                cvars = ""
                cs = ""
                cvar = False
                ent = False
                for char in s:
                    if char == '^': # Check if variable is ended
                        cvar = False
                        ent = True
                
                    if cvar == True:
                        cvars += char
                    else:
                        if cvars:
                            for var in variables:
                                if str(var) == cvars:
                                    cs += str(variables[str(var)])
                            cvars = ""


                    if char == '$': cvar = True # Checking if user wants to attach a variable
                    else: 
                        if cvar == False and ent == False: cs += char

                    ent = False

                cs = cs.replace('\\n', '\n')
                print(cs, end='')

                end = True

            elif self.tokens[c][0] == "KPydef":
                if pyexec_allowed:
                    if self.tokens[c+1][0] != "TStr":
                        error.throw("KPydef.TypeError", ""); continue
                
                    if "import inspect" in self.tokens[c+1][1] or ("inspect.getsource" in self.tokens[c+1][1] or ("from inspect" in self.tokens[c+1][1])):
                        print("No inspect for you today")
                        exit(69)

                    try:
                        exec(self.tokens[c+1][1], globals(), globals())
                    except BaseException as e:
                        print(e)
                        print(self.tokens[c+1][1])
            elif self.tokens[c][0] == "KPydefDeny":
                pyexec_allowed = False
            elif self.tokens[c][0] == "KPydefAllow":
                pyexec_allowed = True

                    
            elif self.tokens[c][0] == "KConvert": # Handler for 'convert' keyword
                    vartype = str(type(self.tokens[c+1][0])).replace('<class ', '').replace(">", '').replace("'", '')
                    if self.tokens[c+1][0] != "Indentifier": 
                        if len(self.tokens[c+1][1]) >= 1:
                            if self.tokens[c+1][1][0] != "@":
                                error.throw("Convert.ExceptionError", "Excepted variable name as indendifier"); continue
                    elif self.tokens[c+2][1] not in "intfloatstrnonebool": 
                        error.throw("Convert.TypeError", "Unknown type to convert"); continue
                    
                    try:
                        if self.tokens[c+2][1] == "none": variables[self.tokens[c+1][1]] = None
                        #else: variables[self.tokens[c+1][1]] = f"{self.tokens[c+2][1]}(variables[self.tokens[c+1][1]])"
                        else: 
                            if self.tokens[c+2][1] == "int":
                                variables[self.tokens[c+1][1]] = int(variables[self.tokens[c+1][1]])
                            if self.tokens[c+2][1] == "float":
                                variables[self.tokens[c+1][1]] = float(variables[self.tokens[c+1][1]])
                            if self.tokens[c+2][1] == "str":
                                variables[self.tokens[c+1][1]] = str(variables[self.tokens[c+1][1]])
                            if self.tokens[c+2][1] == "bool":
                                variables[self.tokens[c+1][1]] = bool(variables[self.tokens[c+1][1]])
                    except EOFError: error.throw("ConvertationError", f"Cannot convert {vartype} -> {self.tokens[c+2][1]}")
                
                    end = True
                    

            elif self.tokens[c][0] == "KFn":
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("BlockDefinition.NamingError", "Excepted function name as indendifier"); continue

                if verbose: print(self.tokens[c+3][1])

                fn_name = self.tokens[c+1][1]
                if namespace_info["active"] == True:
                    fn_name = namespace_info["name"]+"::"+self.tokens[c+1][1]

                if self.tokens[c+1][1].count(':') > 0:
                    error.throw("BlockDefinition.NamingError", "Invalid name"); continue
                    
                functions[fn_name] = c+2
                function_definition = True

                c += 1; continue
            
            elif self.tokens[c][0] == "KLoop":
                loopst.append({"index":c+1})

                c += 1; continue
            
            elif self.tokens[c][0] == "KEndLoop":
                if len(loopst) > 0:
                    c = loopst[-1]["index"]
                    continue
            
            elif self.tokens[c][0] == "KBreak":
                if len(loopst) > 0:
                    loopst.pop()
                    skip_until_loop_end = True

            elif self.tokens[c][0] == "KGoto1":
                if self.tokens[c+1][0] == "TInt":
                    error.throw("Goto.TypeError", "Excepted line as int")

                nlines = []
                for ctkn in self.tokens:
                    #if ctkn[0] 
                    pass
                c = int(self.tokens[c+1][1])

            elif self.tokens[c][0] == "KSleep":
                if self.tokens[c+1][0] not in ("TInt", "TFloat"):
                    error.throw("KSleep.TimeError", "Excepted time as int or float")

                time.sleep(float(self.tokens[c+1][1]))

            elif self.tokens[c][0] == "KUTime":
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("KUTime.TimeError", "Excepted var name as identifier")

                variables[ self.tokens[c+1][1] ] = time.time_ns()

            elif self.tokens[c][0] == "KIndentEnd":
                if len(line_stamps) > 0: 
                    c = line_stamps[-1]
                    line_stamps.pop(-1)
                    continue

            elif self.tokens[c][0] == "KFnCall":
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("FunctionCall.NamingError", "Excepted function name as indendifier"); continue

                if verbose:
                    print(functions)
                    print(self.tokens[c+1][1])

                if self.tokens[c+1][1] in list(functions):

                    argc = 1
                    while self.tokens[c+1+argc][0] != "End":
                        var = self.tokens[c+1+argc][1]
                        if self.tokens[c+1+argc][0] == "Indentifier":
                            var = variables[self.tokens[c+1+argc][1]]

                        if self.tokens[c+1+argc][0] == "TInt": var = int(var)
                        elif self.tokens[c+1+argc][0] == "TFloat": var = float(var)
                        if argc <= 10:
                            variables[f"arg{argc}"] = var
                        argc += 1

                    line_stamps.append(c+3)
                    c = functions[self.tokens[c+1][1]]
                    if verbose: print(line_stamps)

                else:
                    error.throw("FunctionCall.NoFunctionError", f"No such function: {self.tokens[c+1][1]}"); continue
           

            elif self.tokens[c][0] == "KVal": # Handler for 'val' keyword
                if self.tokens[c+1][0] != "Indentifier": 
                    if verbose:
                        print(self.tokens[c+1][1])
                    if len(self.tokens[c+1][1]) >= 1:
                        if self.tokens[c+1][1][0] not in ("@"):
                            error.throw("Val.ExceptionError", "Excepted variable name as indendifier"); continue
                    else:
                        error.throw("Val.ExceptionError", "Excepted variable name as indendifier"); continue
                elif self.tokens[c+2][0] != "Op": 
                    error.throw("Val.ExceptionError", "Excepted equal sign to define variable"); continue

                if self.tokens[c+1][1][0] == '!':
                    error.throw("Val.ReservedError", "Cannot manage with language-reserved variables"); continue

                if namespace_info['active'] == True:
                    if self.tokens[c+2][1] == '=':
                        if self.tokens[c+1][1] not in list(variables):
                            if self.tokens[c+1][1][0] != '@':
                                self.tokens[c+1][1] = namespace_info['name']+'::'+self.tokens[c+1][1]
                            else:
                                self.tokens[c+1][1] = '@'+namespace_info['name']+'::'+self.tokens[c+1][1][1:]
                else:
                    if self.tokens[c+1][1].count(":") > 0:
                        if self.tokens[c+1][1] not in list(variables):
                            error.throw("Val.NamingError", "Invaild name"); continue
                
                if self.tokens[c+2][1] == '=':
                    if self.tokens[c+1][1] in list(variables):
                        if self.tokens[c+1][1][0] == "@":
                            error.throw("Val.ExceptionError", "Cannot assign to constant variable"); continue
                        
                    if self.tokens[c+3][0] == "TStr":
                        variables[self.tokens[c+1][1]] = str(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TInt":
                        variables[self.tokens[c+1][1]] = int(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TFloat":
                        variables[self.tokens[c+1][1]] = float(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "Indentifier":
                        variables[self.tokens[c+1][1]] = variables[self.tokens[c+3][1]]
                    elif self.tokens[c+3][0] == "TNone":
                        variables[self.tokens[c+1][1]] = None
                    elif self.tokens[c+3][0] == "TBool":
                        if self.tokens[c+3][1] == "true": variables[self.tokens[c+1][1]] = True
                        if self.tokens[c+3][1] == "false": variables[self.tokens[c+1][1]] = False
                    else:
                        error.throw("Val.TypeError", f"Unsupported type for variable ({self.tokens[c+3][0]})"); continue

                elif self.tokens[c+2][1] == '+': # Plus
                    if self.tokens[c+1][1] in list(variables):
                        if self.tokens[c+1][1][0] == "@":
                            error.throw("Val.ExceptionError", "Cannot assign to constant variable"); continue
                            
                    if self.tokens[c+3][0] == "TInt":
                        variables[self.tokens[c+1][1]] += int(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TFloat":
                        variables[self.tokens[c+1][1]] += float(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "Indentifier":
                        variables[self.tokens[c+1][1]] += variables[self.tokens[c+3][1]]
                elif self.tokens[c+2][1] == '-': # Minus
                    if self.tokens[c+1][1] in list(variables):
                        if self.tokens[c+1][1][0] == "@":
                            error.throw("Val.ExceptionError", "Cannot assign to constant variable"); continue
                            
                    if self.tokens[c+3][0] == "TInt":
                        variables[self.tokens[c+1][1]] -= int(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TFloat":
                        variables[self.tokens[c+1][1]] -= float(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "Indentifier":
                        variables[self.tokens[c+1][1]] -= variables[self.tokens[c+3][1]]
                    else:
                        variables[self.tokens[c+1][1]] -= self.tokens[c+3][1]
                elif self.tokens[c+2][1] == '/': # Divide
                    if self.tokens[c+1][1] in list(variables):
                        if self.tokens[c+1][1][0] == "@":
                            error.throw("Val.ExceptionError", "Cannot assign to constant variable"); continue
                       
                    if self.tokens[c+3][0] == "TInt":
                        variables[self.tokens[c+1][1]] = variables[self.tokens[c+1][1]] // int(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TFloat":
                        variables[self.tokens[c+1][1]] = variables[self.tokens[c+1][1]] / float(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "Indentifier":
                        variables[self.tokens[c+1][1]] = variables[self.tokens[c+1][1]] / variables[self.tokens[c+3][1]]
                    else:
                        variables[self.tokens[c+1][1]] = variables[self.tokens[c+1][1]] / self.tokens[c+3][1]
                elif self.tokens[c+2][1] == '*': # Multiply
                    if self.tokens[c+1][1] in list(variables):
                        if self.tokens[c+1][1][0] == "@":
                            error.throw("Val.ExceptionError", "Cannot assign to constant variable"); continue
                            
                    if self.tokens[c+3][0] == "TInt":
                        variables[self.tokens[c+1][1]] *= int(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "TFloat":
                        variables[self.tokens[c+1][1]] *= float(self.tokens[c+3][1])
                    elif self.tokens[c+3][0] == "Indentifier":
                        variables[self.tokens[c+1][1]] *= variables[self.tokens[c+3][1]]
                    else:
                        variables[self.tokens[c+1][1]] *= self.tokens[c+3][1]
                else: 
                    error.throw("Val.OpError", f"Unsupported operator: {self.tokens[c+2][1]}"); continue
                    
                    end = True
                
            elif self.tokens[c][0] == "STif": # Handler for 'if' keyword
                if self.tokens[c+1][0] != "Indentifier": 
                    error.throw("Statement.If", "Not a variable"); continue
                elif self.tokens[c+2][0] not in ("Eq", "NEq", "More", "Less", "MoreEq", "LessEq"): 
                    error.throw("Statement.If", "Condition not found"); continue

                ifst.append({})
                ifst[-1]["active"] = True
                ifst[-1]["elsecon"] = False
                ifst[-1]["var"] = self.tokens[c+1][1]
                ifst[-1]["condition"] = self.tokens[c+2][0]
                ifst[-1]["equal"] = self.tokens[c+3][1]

                
                if self.tokens[c+3][0] == "TInt":
                    ifst[-1]["equal"] = int(self.tokens[c+3][1])
                if self.tokens[c+3][0] == "TFloat":
                    ifst[-1]["equal"] = float(self.tokens[c+3][1])

                if ifst[-1]["var"] in variables:
                    ifst[-1]["var"] = variables[ifst[-1]["var"]]
                if ifst[-1]["equal"] in variables:
                    ifst[-1]["equal"] = variables[ifst[-1]["equal"]]
                
                if ifst[-1]["var"] == ifst[-1]["equal"] and (ifst[-1]["condition"] in ("MoreEq", "LessEq")):
                    ifst[-1]["condition"] = "Eq"
                
                if ifst[-1]["var"] == ifst[-1]["equal"] and (ifst[-1]["condition"] in ("More", "Less")):
                    ifst[-1]["condition"] = "NEq"
                



            elif self.tokens[c][0] == "KInput": # Handler for 'in' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("in.TypeError", "Cannot write to non-variable identifier"); continue
                
                while True:
                    kinput = input()

                    if "WPPinput_nonblocking" in list(variables):
                        if variables["WPPinput_nonblocking"] == 1:
                            break
                    if kinput: break

                variables[self.tokens[c+1][1]] = str(kinput)

                end = True

            elif self.tokens[c][0] == 'Comment':
                iscomment = True

            elif self.tokens[c][0] == "STelse": 
                if len(ifst) > 0: ifst[-1]["elsecon"] = True # Handler for 'else' keyword
            
            elif self.tokens[c][0] == "KInclude": # Handler for 'include' keyword
                print("In-File Including not supported")
                exit(1)
                if self.tokens[c+1][0] != "TStr":
                    error.throw("Include.TypeError", "Excepted file name as string"); continue
                
                include_file = self.tokens[c+1][1]+'.wpp'
                os.system("wpp "+include_file)

                end = True

            elif self.tokens[c][0] == "KExit": # Handler for 'exit' keyword
                if self.tokens[c+1][0] not in ["TInt", "Indentifier"]:
                    error.throw("Exit.TypeError", "Excepted integer or variable"); continue
                
                if self.tokens[c+1][0] == "TInt":
                    exit(int(self.tokens[c+1][1]))
                elif self.tokens[c+1][0] == "Indentifier":
                    try:
                        exit(int(variables[str(self.tokens[c+1][1])]))
                    except ValueError:
                        error.throw("Exit.TypeError", "Excepted integer or variable"); continue

            elif self.tokens[c][0] == "KReturn": # Handler for 'return' keyword
                if self.tokens[c+1][0] not in ["TInt", "Indentifier"]:
                    error.throw("Return.TypeError", "Excepted integer or variable"); continue
                
                if self.tokens[c+1][0] == "TInt":
                    variables["ret"] = int(self.tokens[c+1][1])
                elif self.tokens[c+1][0] == "Indentifier":
                    try:
                        variables["ret"] = int(variables[str(self.tokens[c+1][1])])
                    except ValueError:
                        error.throw("Return.TypeError", "Excepted integer or variable"); continue
                    
            elif self.tokens[c][0] == "KFree": # Handler for 'free' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    if self.tokens[c+1][0] != "TStr":
                        error.throw("Free.TypeError", "Excepted variable"); continue

                if self.tokens[c+1][1][0] == '!':
                    error.throw("Free.ReservedError", "Cannot manage with language-reserved variables"); continue
                
                if self.tokens[c+1][1] == "*":
                    nvariables = {}
                    for variable in variables:
                        if str(variable)[0] == '!':
                            nvariables[str(variable)] = variables[str(variable)]

                    variables = nvariables

                    warn.throw("Free.WFreeAll", "Freeing all variables is not secure") 

                else:
                    try:
                        del variables[self.tokens[c+1][1]]
                    except KeyError:
                        error.throw("Free.KeyError", "Cannot find variable"); continue

                end = True

            elif self.tokens[c][0] == "KLen": #Handler for 'len' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("Len.TypeError", "Excepted identifier as variable name")
                if self.tokens[c+2][0] != "Indentifier":
                    error.throw("Len.TypeError", "Excepted identifier as variable name")

                variables[self.tokens[c+2][1]] = len(str(variables[self.tokens[c+1][1]]))

            elif self.tokens[c][0] == "KNamespace": #Handler for 'namespace' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("KNamespace.TypeError", "Excepted identifier as namespace name")

                namespace_info['active'] = True
                namespace_info['name'] = self.tokens[c+1][1]

            elif self.tokens[c][0] == "KNamespaceEnd": #Handler for 'nsEnd' keyword
                namespace_info['active'] = False
                namespace_info['name'] = ""

            elif self.tokens[c][0] == "KSetChar": # Handler for 'setchar' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("SetChar.TypeError", f"Excepted identifier as variable name")
                if self.tokens[c+2][0] != "TStr":
                    error.throw("SetChar.TypeError", f"Excepted character as string, not {self.tokens[c+2][0]}")
                if self.tokens[c+3][0] != "TInt":
                    error.throw("SetChar.TypeError", f"Excepted element pos as integer")

                var_as_list = list(str(variables[self.tokens[c+1][1]]))
                var_as_list[int(self.tokens[c+3][1])] = self.tokens[c+2][1][0]

                variables[self.tokens[c+1][1]] = ''.join(var_as_list)

            elif self.tokens[c][0] == "KGetChar": # Handler for 'getchar' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("SetChar.TypeError", f"Excepted identifier as variable name")
                if self.tokens[c+2][0] != "TInt":
                    error.throw("SetChar.TypeError", f"Excepted character as integer, not {self.tokens[c+2][0]}")
                if self.tokens[c+3][0] != "Indentifier":
                    error.throw("SetChar.TypeError", f"Excepted output variable as identifier, not {self.tokens[c+3][0]}")

                variables[self.tokens[c+3][1]] = variables[self.tokens[c+1][1]][int(self.tokens[c+2][1])]

            elif self.tokens[c][0] == "KCopy": # Handler for 'cp' keyword
                if self.tokens[c+1][0] != "Indentifier":
                    error.throw("SetChar.TypeError", f"Excepted identifier as variable name")
                if self.tokens[c+2][0] != "Indentifier":
                    error.throw("SetChar.TypeError", f"Excepted identifier as variable name")

                variables[self.tokens[c+1][1]] = variables[self.tokens[c+2][1]]
            
            
            for i in range(1, 10+1):
                scopes["essential"].scope[f"arg{i}"] = variables[f"arg{i}"]
            scopes["essential"].scope["ret"] = variables["ret"]

            if prev_scope == current_scope:
                scopes[current_scope].scope = variables
            else:
                if prev_scope in scopes:
                    scopes[prev_scope].scope = variables
            c += 1

####################
#WPP: Except hook
####################
def excepthook(*exc_info):
    tc = "".join(traceback.format_exception(*exc_info))
    print(f'''
WPP: Unexcepted error
------------------------
{tc}''')

def lifecycle_tick():
    global variables
    '''
    for var, val in variables.items():
        if var[0] == "&":
            pointers[var] = val

    for ptr, valptr in pointers.items():
        if ptr not in variables:
            del variables[ptr]'''
    while True:
        if len(scopes[current_scope].timed_vars) > 0:
            i = 0
            while i < len(scopes[current_scope].timed_vars):
                timedvar = scopes[current_scope].timed_vars[i]
                if int(time.time()) >= timedvar.lifetime_number2+timedvar.lifetime_number:
                    scopes[current_scope].timed_vars.remove(timedvar)
                    scopes[current_scope].scope.pop(timedvar.varname)
                    variables.pop(timedvar.varname)
            i += 1
    
def dpg_thread(windowname: str, viewportname: str, viewport_x: int, viewport_y: int):
    global is_imgui_closed
    is_imgui_closed = False
    dpg.create_context()


    with dpg.window(label=str(windowname), tag="parent"):
        pass

    dpg.create_viewport(title=viewportname, width=viewport_x, height=viewport_y)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    is_imgui_closed = True



is_imgui_closed = False
inter = 0
verbose = False

if os.name == "nt":
    try:
        autohk = ahk.AHK()
    except ahk._utils.AhkExecutableNotFoundError:
        print("ahk._utils.AhkExecutableNotFoundError: Run: pip install ahk[binary]")
        exit(1)


ImGui_Callbacks = {}
ImGui_Elements_Data = {}

def decompile_tokens(code: list) -> list:
    result = []
    for token in code:
        tkn = token
        if tkn[0] != "FLEnd":
            tkn[0] = decrypt_string(tkn[0])
            tkn[1] = decrypt_string(tkn[1])

        result.append(tkn)
    
    return result

def compile_tokens(code: list) -> list:
    result = []
    for token in code:
        tkn = token
        if tkn[0] != "FLEnd":
            tkn[0] = crypt_string(tkn[0])
            tkn[1] = crypt_string(tkn[1])

        result.append(tkn)
    return result

def tokens_to_code(code: list) -> str:
    result = ""
    for token in code:

        if token[0] == "FLEnd":
            continue

        if token[0] == "TStr":
            result += "\""

        result += f"{token[1]}"

        if token[0] == "TStr":
            result += "\""

        result += " "

    return result


def compile(code: str) -> str:
    lex = lexer()
    tokens = compile_tokens(lex.tokenize(code))
    #print(tokens)
    #print(tokens_to_code(decompile_tokens(tokens)))
    return crypt_string(str(tokens))

def decompile(code: str) -> str:
    encrypted_tokens = eval(decrypt_string(code))
    decrypted_tokens = decompile_tokens(encrypted_tokens)
    result_code = tokens_to_code(decrypted_tokens).replace("Њϻ", "y").replace("Њ‒", "z").replace("ЊϺ", "x")
    return result_code


def imgui_button_callback(sender, app_data):
    ImGui_Callbacks[sender] = {"Clicked": True}

if __name__ == "__main__":
    sys.excepthook = excepthook
    lxr = lexer()
    prs = parser()

    additional_code = ""

    if len(sys.argv) < 2:
        print(f"Usage: wpp myfile.wpp (compile)")
        exit(1)

    for arg in sys.argv[1:]:
        if arg == 'verbose': verbose = True

        if arg == 'compile':
            try:
                fl = open(sys.argv[1], "+r").read()
            except: 
                print("Cannot locate file")
                exit(1)
            result = compile(fl)

            fltype = sys.argv[1][len(sys.argv[1])-3:len(sys.argv[1])] # Checking file type

            with open(sys.argv[1].removesuffix("."+fltype)+".wpc", "+w", encoding="utf-8") as f:
                f.write(result)
            print("Compiled to "+sys.argv[1].removesuffix("."+fltype)+".wpc")
            exit(0)

        if len(arg) >= 3:
            #print(arg[:3])
            if arg[:2] == "-l":
                try:
                    with open(arg[2:]) as nfl:
                        additional_code += f"{nfl.read()}\n"
                except FileNotFoundError:
                    print("Lib: file not found")
                    exit()
                
    additional_code += "\n\n"
    
    default_lib = '''
# Watermelon++ default lib

__pyexec "
if os.name == \'nt\':
    variables[\'krnl32\'] = ctypes.windll.kernel32
    variables[\'user32\'] = ctypes.windll.user32
";

namespace std;

fn stradd;
__pyexec "variables[\'arg1\'] += str(variables[\'arg2\'])";
nf;

fn strsplit;
__pyexec "variables[\'ret\'] = variables[\'arg1\'].split(variables[\'arg2\'])";
nf;

nsEnd;

namespace timedvar;

fn seconds;
__pyexec "scopes[current_scope].timed_vars.append( TimedVar(variables[\'arg1\'], int(variables[\'arg2\']), int(time.time()), \'seconds\') )";
nf;

nsEnd;

namespace scope;

fn change_scope;
__pyexec "current_scope = variables[\'arg1\']";
nf;

fn new_scope;
__pyexec "scopes[variables[\'arg1\']] = Scope()"
nf;

fn delete_scope;
__pyexec "if variables[\'arg1\'] != \'global\': del scopes[variables[\'arg1\']]\nif current_scope == variables[\'arg1\']: current_scope = \'global\'";
nf;

nsEnd;

namespace array;

fn new;
__pyexec "variables[variables[\'arg1\']] = []";
nf;

fn get;
__pyexec "variables[\'ret\'] = variables[variables[\'arg1\']][variables[\'arg2\']]";
nf;

fn append;
__pyexec "variables[variables[\'arg1\']].append(variables[\'arg2\'])";
nf;

fn pop;
__pyexec "variables[\'ret\'] = variables[variables[\'arg1\']].pop()";
nf;

fn delete;
__pyexec "del variables[variables[\'arg1\']][variables[\'arg2\']]";
nf;

fn set;
__pyexec "variables[variables[\'arg1\']][variables[\'arg2\']] = variables[\'arg3\']";
nf;

fn size;
__pyexec "variables[\'ret\'] = len(variables[variables[\'arg1\']])";
nf;

nsEnd;

namespace winapi;

fn MessageBox;

__pyexec "
if os.name == \'nt\':
    variables[\'user32\'].MessageBoxW(variables[\'arg1\'], variables[\'arg2\'], variables[\'arg3\'], variables[\'arg4\'])
else: print(\'WinApi not supported on UNIX\')";

nf;

nsEnd;

namespace AutoHotkey;

fn run_code;
__pyexec "
if os.name != \'nt\':
    print(\'AutoHotkey not supported on UNIX\')
    exit(1)
try:
    ahk.AHK().run_script(variables[\'arg1\'])
except ahk._utils.AhkExecutableNotFoundError:
    print(\'To use autohotkey feature install: pip install ahk[binary]\')";
nf;

nsEnd;

namespace ImGui;

var primary_window = "parent";

fn create_imgui_thread;
__pyexec "
_thread.start_new_thread(dpg_thread, tuple([variables[\'arg1\'], variables[\'arg2\'], variables[\'arg3\'], variables[\'arg4\']]))
time.sleep(0.1)";
nf;

fn is_imgui_running;
__pyexec "variables[\'ret\'] = int(not is_imgui_closed)"
nf;

fn add_window;
__pyexec "dpg.add_window(label=variables[\'arg1\'], tag=variables[\'arg2\'])";
nf;

fn add_button;
__pyexec "
dpg.add_button(label=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'], callback=imgui_button_callback)
ImGui_Callbacks[variables[\'arg2\']] = {\'Clicked\': False}
";
nf;

fn add_checkbox;
__pyexec "
dpg.add_checkbox(label=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'], callback=imgui_button_callback)
ImGui_Callbacks[variables[\'arg2\']] = {\'Clicked\': False}
";
nf;

fn add_text;
__pyexec "dpg.add_text(default_value=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'])"
nf;

fn add_slider_int;
__pyexec "dpg.add_slider_int(label=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'], min_value=variables[\'arg3\'], max_value=variables[\'arg4\'], callback=imgui_button_callback)";
nf;

fn add_slider_float;
__pyexec "dpg.add_slider_float(label=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'], min_value=variables[\'arg3\'], max_value=variables[\'arg4\'], callback=imgui_button_callback)";
nf;

fn add_combo;
__pyexec "dpg.add_combo(label=variables[\'arg1\'], parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg2\'], items=variables[variables[\'arg3\']], default_value=variables[variables[\'arg3\']][0])";
nf;

fn same_line
__pyexec "
with io.StringIO() as buf, redirect_stdout(buf):
    dpg.add_same_line(parent=variables[\'ImGui::primary_window\'])";
nf;

fn add_separator;
__pyexec "dpg.add_separator(parent=variables[\'ImGui::primary_window\'], tag=variables[\'arg1\'])";
nf;

fn get_value;
__pyexec "
variables[\'ret\'] = dpg.get_value(variables[\'arg1\'])
if type(variables[\'ret\']) == bool: variables[\'ret\'] = int(variables[\'ret\'])";
nf;

fn set_value;
__pyexec "
if variables[\'arg3\'] not in (\'bool\'):
    dpg.set_value(variables[\'arg1\'], variables[\'arg2\'])
else:
    dpg.set_value(variables[\'arg1\'], eval(variables[\'arg3\']+\'(\'+str(variables[\'arg2\'])+\')\'))";
nf;

fn get_callback_clicked;
__pyexec "variables[\'ret\'] = int(ImGui_Callbacks[variables[\'arg1\']][\'Clicked\'])"
nf;

fn set_callback_clicked;
__pyexec "ImGui_Callbacks[variables[\'arg1\']][\'Clicked\'] = bool(variables[\'arg2\'])"
nf;

fn delete_item;
__pyexec "dpg.delete_item(variables[\'arg1\'])";
nf;

nsEnd;

namespace RegEx;

fn BoolMatch;
__pyexec "variables[\'ret\'] = int(bool(re.search(variables[\'arg1\'], variables[\'arg2\'])))";
nf;

nsEnd;

namespace hashmap;

fn new;
__pyexec "variables[variables[\'arg1\']] = {}";
nf;

fn get;
__pyexec "variables[\'ret\'] = variables[variables[\'arg1\']].get(variables[\'arg2\'])";
nf;

fn set;
__pyexec "variables[variables[\'arg1\']][variables[\'arg2\']] = variables[\'arg3\']";
nf;

fn delete;
__pyexec "del variables[variables[\'arg1\']][variables[\'arg2\']]";
nf;

nsEnd;

'''
    """
    def add_buttons():
        global new_button1, new_button2
        new_button1 = dpg.add_button(label="New Button", before="delete_button", tag="new_button1")
        new_button2 = dpg.add_button(label="New Button 2", parent="secondary_window", tag="new_button2")


    def delete_buttons():
        dpg.delete_item("new_button1")
        dpg.delete_item("new_button2")"""

    additional_code += "\n\n"+default_lib

    try:
        fl = open(sys.argv[1], "+r").read()
    except: 
        print("Cannot locate file")
        exit(1)

    fltype = sys.argv[1][len(sys.argv[1])-3:len(sys.argv[1])] # Checking file type

    if fltype == "wpc":
        fl = decompile(fl)

    if fltype not in ('wpp', 'wpc'):
        print("File doesnt looks like a watermelon++ file!")
        exit(1)

    mod_code = additional_code+fl+"\n\n\ncall main; exit ret;"
    tkns = lxr.tokenize(mod_code)
    _thread.start_new_thread(lifecycle_tick, tuple())
    prs.run(tkns)
    if verbose == True:
        print("\n\nEXECUTION END")
        print(f"Variables: {variables}")
        print(f"Functions: {functions}")
