from dataclasses import dataclass, field
from typing import Type
from ..dev.Terminate import *

@dataclass
class CMakeCommandKeyArguments:
    _key : str
    _args : list = field(default_factory=list)
    def __init__(self, key:str, *args):
        self._key = key if isinstance(key, str) else terminate("key must be string")
        if not isinstance(args, tuple):
            terminate(" args must be list")
        
        # Handle case for when args tuple contain a list
        if len(args) > 0 and isinstance(args[0], list):
            all_list = list()
            for arg in args:
                if isinstance(arg, list)  :
                    all_list.extend(arg)
            args = tuple(all_list)
                    
        if not all(isinstance(arg, str) for arg in args): 
            stringified_args = list()
            for arg in args:
                if arg is not str:
                    stringified_args.append(str(arg))
                else :
                    stringified_args.append(arg)
            self._args = stringified_args                
        else:             
            self._args = args
    
    def __str__(self):
        return str.format(
            "{}",            
            self.getStr_singleline() if len(self._args) < 2 else self.getStr_multiline()
        )
    
    def getStr_custom(self, joinStr):        
        return str.format(
            "{} {}",
            self._key,
            joinStr.join(self._args)
        )

    def getStr_singleline(self):        
        return str.format(
            "{} {}",
            self._key,
            ' '.join(self._args)
        )

    def getStr_multiline(self):        
        return str.format(
            "{} {}",
            self._key,
            '\n\t'+'\n\t'.join(self._args)
        )

@dataclass
class CMakeCommandKeyArguments_str(CMakeCommandKeyArguments):
    def __init__(self, key:str, *args):
        self.stringifyArgs(args)
        super().__init__(key, *self._args)        

    def stringifyArgs(self, args):
        self._args = tuple("\""+arg+"\"" for arg in args)

@dataclass
class CMakeCommandKeyArguments_FuncArgs(CMakeCommandKeyArguments):
    def __init__(self, *args):
        super().__init__("", *args)        

class CMakeCommandMeta(type):
    def __new__(cls, name, bases, dct):
        if name[:4] == "CMC_":
            dct['commandName'] = name[4:] # remove the first "CMC_" of the CMakeCommand
        elif name[:5]  == "CMCC_":
            dct['commandName'] = name[5:] # remove the first "CMCC_" of the CMakeCommand
        elif name == "CMakeCommand" or name == "CMakeCommandContainer": 
            pass
        elif name == "CMC_CALLFUNC": 
            pass 
        else: 
            terminate("name of a CMakeCommand subclass must start with CMC_ or CMCC_")
        if "__str__" not in dct:
            #sets the __str__ method of a subclass to be the same as the basclass (i.e. CMakeCommand)
            dct['__str__'] = bases[0].__str__

        if "__init__" not in dct:
            #sets the __init__ method of a subclass to be the same as the basclass (i.e. CMakeCommand)
            dct['__init__'] = bases[0].__init__
            
        return super().__new__(cls, name, bases, dct)

CMCK = CMakeCommandKeyArguments                 # Shorthand 
CMCK_str = CMakeCommandKeyArguments_str         # Adds \"\" around strings 
CMCK_args = CMakeCommandKeyArguments_FuncArgs   # Ignores the key argument...
@dataclass
class CMakeCommand(metaclass=CMakeCommandMeta): #CMC for short
    commandName :str
    commandArgVals : list = field(default_factory=list)

    def add_commandArgVals(self, commandArgVals : list):
        if not isinstance(commandArgVals, tuple):
            terminate("args must be tuple")
        self.commandArgVals = commandArgVals if all(isinstance(arg, CMakeCommandKeyArguments) or isinstance(arg, CMakeCommandKeyArguments_str) for arg in commandArgVals) else terminate("args must be a CMakeCommandKeyArguments, aka CMCK" )        

    def __init__(self, *CMC_CKeyArgs ):        
        self.add_commandArgVals(CMC_CKeyArgs)


    def __str__(self):
        return str.format(
            "{}({})",
            self.commandName,
            ' '.join(map(str, self.commandArgVals)) if len(self.commandArgVals) < 3 else '\n\t'.join(map(str, self.commandArgVals))
        )

@dataclass
class CMakeCommandContainer(metaclass=CMakeCommandMeta):
    commandName :str
    baseArgs : CMakeCommandKeyArguments  = field(default_factory=CMakeCommandKeyArguments)
    containerContent : list = field(default_factory=list)

    def add_containerContent(self, containerContents : list): #TODO: Should be tuple! (?)
        if not isinstance(containerContents, tuple):
            terminate("containerContents must be tuple")
        self.containerContent = containerContents if all(isinstance(arg, CMakeCommand) for arg in containerContents) else terminate("args must be a CMakeCommand")        

    def __init__(self, CMC_args :CMakeCommandKeyArguments ,*CMC_cs ):
        self.baseArgs = CMC_args
        self.add_containerContent(CMC_cs)

    def __str__(self):
        return str.format(
            "{}({})\n\t{}\n{}()",
            self.commandName,
            ' '.join(map(str, self.baseArgs)),
            ' '.join(map(str, self.containerContent)) if len(self.containerContent) < 3 else '\n\t'.join(map(str, self.containerContent)),
            "end" + self.commandName # NOTE: Might exist cases where the scope does not end with <key>() \n <body contents> \n end<key>() ...
        )
