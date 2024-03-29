from dataclasses import dataclass, field
from typing import Optional

from ..dev.Terminate import terminate

@dataclass
class CPPCommandKeyArguments: #TODO: Check if we can reuse the CMakeCommandKeyArguments...
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
            self._args = list(args)
    
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
class CPPCommandKeyArguments_str(CPPCommandKeyArguments):
    def __init__(self, key:str, *args):
        self.stringifyArgs(args)
        super().__init__(key, *self._args)        

    def stringifyArgs(self, args):
        self._args = list("\""+arg+"\"" for arg in args)

@dataclass
class CPPCommandKeyArguments_FuncArgs(CPPCommandKeyArguments):
    def __init__(self, *args):
        super().__init__("", *args)        



class CPPCommandMeta(type):
    def __new__(cls, name, bases, dct):
        if name[:4] == "CPP_":
            dct['commandName'] = name[4:] # remove the first "CPP_" of the CMakeCommand
        elif name[:5]  == "CPPC_":
            dct['commandName'] = name[5:] # remove the first "CPPC_" of the CMakeCommand
        elif name == "CPPCommand" or name == "CPPCommandContainer": 
            pass
        elif name == "CPP_INCLUDE_SYS" or name == "CPP_INCLUDE_USR": 
            pass #dct['commandName'] = name[5:]
        else: 
            terminate("name of a CMakeCommand subclass must start with CPP_ or CPPC_")
        if "__str__" not in dct:
            #sets the __str__ method of a subclass to be the same as the basclass (i.e. CPPCommand)
            dct['__str__'] = bases[0].__str__

        if "__init__" not in dct:
            #sets the __init__ method of a subclass to be the same as the basclass (i.e. CPPCommand)
            dct['__init__'] = bases[0].__init__
            
        return super().__new__(cls, name, bases, dct)

CPPCK       = CPPCommandKeyArguments            # Shorthand 
CPPCK_str   = CPPCommandKeyArguments_str        # Adds \"\" around strings 
CPPCK_args  = CPPCommandKeyArguments_FuncArgs   # Ignores the key argument...
@dataclass
class CPPCommand(metaclass=CPPCommandMeta): #CPP for short
    commandName :str
    commandArgVals : list = field(default_factory=list)

    def add_commandArgVals(self, commandArgVals : list):
        if not isinstance(commandArgVals, list):
            terminate("args must be tuple")
        self.commandArgVals = commandArgVals if all(isinstance(arg, CPPCK) or isinstance(arg, CPPCK_str) or isinstance(arg, CPPCK_args) for arg in commandArgVals) else \
        terminate("args must be a CPPCommandKeyArguments, aka CPPCK" )        

    def __init__(self, *CPP_CKeyArgs ):        
        self.add_commandArgVals(list(CPP_CKeyArgs))


    def __str__(self):
        return str.format(
            "{}({})",
            self.commandName,
            ', '.join(map(str, self.commandArgVals)) if len(self.commandArgVals) < 3 else '\n\t'.join(map(str, self.commandArgVals))
        )

@dataclass
class CPPCommandContainer(metaclass=CPPCommandMeta):
    commandName :str
    baseArgs : CPPCK 
    containerContent : list = field(default_factory=list)
    identifier : str = ""

    def add_containerContent(self, containerContents : list):
        if not isinstance(containerContents, list):
            terminate("containerContents must be tuple")
        if not hasattr(self, 'containerContent'):
            self.containerContent = []
        self.containerContent.extend(containerContents if all(isinstance(arg, CPPCommand) for arg in containerContents) else terminate("args must be a CPPCommand"))

    def __init__(self, CPP_args  ,*CMC_cs, identifier :Optional[str] = "" ):
        self.baseArgs = CPP_args
        self.identifier = identifier
        self.add_containerContent(list(CMC_cs))

    def __str__(self):
        return str.format(
            "{}({})\n{{\n\t{}\n}}",
            self.commandName,
            (', '.join(map(str, self.baseArgs)) if type(self.baseArgs) is list else self.baseArgs.__str__()),
            '; '.join(map(str, self.containerContent) ) + ";" if len(self.containerContent) < 3 else '\n\t'.join(map(str, self.containerContent)) + ";" ,
            "}}" 
        )


class CPP_INCLUDE_SYS(CPPCommand):
    def __init__(self,*CPP_CKeyArgs):
        super().__init__(*CPP_CKeyArgs)
        self.commandName = "#include"

    def __str__(self):
        return str.format(
            "{} <{}>",
            self.commandName,
            ', '.join(map(str, self.commandArgVals)).strip()
        )

class CPP_INCLUDE_USR(CPPCommand):
    def __init__(self,*CPP_CKeyArgs):
        super().__init__(*CPP_CKeyArgs)
        self.commandName = "#include"

    def __str__(self):
        return str.format(
            "{} \"{}\"",
            self.commandName,
            ', '.join(map(str, self.commandArgVals)).strip()
        )


class CPP_CUSTOMLINE(CPPCommand):
    def __init__(self, *customLineStr : str):
        super().__init__(CPPCK(*customLineStr))        

    def __str__(self):
        return str.format(
            "{}",
            '\n'.join(map(str, self.commandArgVals)).strip()
        )

class CPPC_main(CPPCommandContainer):
    def __init__(self,CPP_args : list[CPPCK],*CPP_CKeyArgs, identifier :Optional[str] = "" ):
        super().__init__(CPP_args, *CPP_CKeyArgs, identifier=identifier)
        self.commandName = "int main"
    
    def __str__(self):
        return str.format(
            "{}({})\n{{\n\t{}\n}}",
            self.commandName,
            (', '.join(map(str, self.baseArgs)) if type(self.baseArgs) is list else self.baseArgs.__str__()),
            ';\n\t'.join(map(str, self.containerContent) ) + ";" ,
            "}}" 
        )



@dataclass
class CPPCommandDct:
    all_cppc : dict = field(default_factory=dict)
    _cpps :   dict = field(default_factory=dict)
    _cpp_cs : dict = field(default_factory=dict)
    _cpp_cs_appended : dict = field(default_factory=dict[type, dict[str,CPPCommandContainer]])
    all_cppc : dict = field(default_factory=dict)

    
    def add_CPP(self, cmc):
        if not issubclass(type(cmc), CPPCommand):
            terminate("Can only add subclass of CPPCommand")
            
        if(type(cmc) not in self._cpps):
            self._cpps.setdefault(type(cmc), [])
            self.all_cppc.setdefault(type(cmc), [])

        self._cpps[type(cmc)].append(cmc)
        self.all_cppc[type(cmc)].append(cmc)
        return cmc


    def add_CPP_C(self, cmc_container):
        if not issubclass(type(cmc_container), CPPCommandContainer):
            terminate("Can only add subclass of CPPCommandContainer")
            
        if(type(cmc_container) not in self._cpps):
            self._cpp_cs.setdefault(type(cmc_container), [])
            self.all_cppc.setdefault(type(cmc_container), [])

        if type(cmc_container) in self._cpp_cs_appended:
            if cmc_container.identifier in self._cpp_cs_appended[type(cmc_container)]:
                for content in self._cpp_cs_appended[type(cmc_container)][cmc_container.identifier]:
                    cmc_container.add_containerContent(content)
                self._cpp_cs_appended[type(cmc_container)][cmc_container.identifier].clear()

        self._cpp_cs[type(cmc_container)].append(cmc_container)
        self.all_cppc[type(cmc_container)].append(cmc_container)
        return cmc_container
    
    def appendTo_CPP_C(self, identifier: str, commandType : type ,commandsToAdd : list[CPPCommand]):
        if not issubclass(commandType, CPPCommandContainer):
            terminate("Can only append to subclasses of CPPCommandContainer")
            
        if(commandType not in self._cpp_cs):
           
            if(commandType not in self._cpp_cs_appended):
                self._cpp_cs_appended.setdefault(commandType, dict[str,list[CPPCommand]]())
                
            if identifier not in self._cpp_cs_appended[commandType]:
                self._cpp_cs_appended[commandType].setdefault(identifier, list[CPPCommand]())

            self._cpp_cs_appended[commandType][identifier].append(commandsToAdd)
        else : 

            for container in self._cpp_cs[commandType]:
                if container.identifier == identifier:
                    container.add_containerContent(commandsToAdd)

    def clear(self):
        self._cpps.clear()
        self._cpp_cs.clear()
        self.all_cppc.clear()

    def __str__(self):
        ret = ""
        for key, value in self._cpps.items() : 
            ret += str(key.__name__) +":\n"
            ret += "\n".join(map(str,value)) + "\n\n"

        return ret