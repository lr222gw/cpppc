from abc import ABCMeta,ABC
import inspect
from typing import Callable, Generic, Tuple, Type, TypeVar,Optional

from ..dev.Terminate import terminate



T = TypeVar('T')
class GenericTypeValueSetterMetaClass(type):

    def __new__(cls, name: str, bases: tuple, dct: dict, classType=None, superRoot=None):
        this = GenericTypeValueSetterMetaClass

        if classType != None and superRoot != None:
            if '__init__' in dct:
                dct['__oldInit__'] = dct['__init__']

            dct['__superRoot'] = superRoot
            dct['__classType'] = classType

            def custom_init(self, *args, **kwargs):
                # if dct['__init__'] != super(self.__class__, self).__init__.__func__: # This occours if a subtype that inherits from the superRoot also is a generic...
                super_class = super(self.__class__, self)
                
                # Appends the required argument, if its missing 
                reqs = this.__getInjectedArguments(super_class,classType, *args, **kwargs)

                super_class.__init__(*reqs, **kwargs)                
                
                this.__validate_initT_onSuperRoot(self,name,bases,superRoot)
                
                # call __initT, if current class inherits from superRoot
                if len(bases) > 0 and bases[0] == superRoot:

                    initT_funcStr = this.__get_initTFunc_str(superRoot)

                    if isinstance(classType, GenericTypeValueSetterMetaClass):
                        f = getattr(self, initT_funcStr)
                        f(classType())
                        
                    else:
                        initT_func = getattr(super_class, initT_funcStr)
                        initT_func(classType)
                
                if '__oldInit__' in dct:
                    dct['__oldInit__'](self,  *args, **kwargs)      

            dct['__init__'] = custom_init

        else: 
            this.__validateClassType(name, bases, classType, superRoot)

        new_class = super().__new__(cls, name, bases, dct)
        super().__init__(new_class, name, bases, dct)

        return new_class

    
    
    @staticmethod
    def __getInjectedArguments(super_class, classType, *args, **kwargs) -> ...:
        init_signature = inspect.signature(super_class.__init__)
        
        # Assuming that the first parameter is the required argument
        requiredLength = len(init_signature.parameters) 
        actualLength = len(args) + len(kwargs)
        reqs = list([classType() for p in init_signature.parameters if type(init_signature.parameters[p].annotation) == TypeVar])
        
        if requiredLength > actualLength:
            reqs += args
        else:
            reqs = args

        return reqs

    @staticmethod
    def __get_initTFunc_str(superRoot):
        initT_funcStr = "_" + superRoot.__name__ + "__initT"
        return initT_funcStr    
    
    @staticmethod
    def __validate_initT_onSuperRoot(instance, instanceName, bases, superRoot):
        this = GenericTypeValueSetterMetaClass

        initT_funcStr = this.__get_initTFunc_str(superRoot)
        if not hasattr(instance, initT_funcStr) and superRoot != None:
            terminate("Missing `initT function` in " +instanceName 
                + " declaration. Add function to class  like this: \n\tclass "  
                + instanceName + "("
                + bases[0].__name__+"[T], metaclass=GenericTypeValueSetter):\n"
                + "\tdef __initT(self, t):\n\t\tself.<YourGenericHere> = t")
    
    @staticmethod
    def __validateClassType(name, bases, classType, superRoot):
        if any(isinstance(base, GenericTypeValueSetterMetaClass) for base in bases ):
            genericParents = list([base for base in bases if isinstance(base, GenericTypeValueSetterMetaClass)])
            parentIsGenericSub = True
            for genericParent in genericParents : 
                if(not hasattr(genericParent, "__superRoot")): 
                    if any(base == Generic for base in bases) :
                        break
                    parentIsGenericSub = False
                    break

            if not parentIsGenericSub:
                missing_classType_str = "`classType`" if classType == None else ""
                missing_superRoot_str = "`superRoot`" if superRoot == None else ""
                missing_str = missing_classType_str + (" and " if missing_classType_str!="" and missing_superRoot_str!="" else "") + missing_superRoot_str
                terminate("Missing "+missing_str+" argument in " +name                 
                            + " declaration. Adjust class signature like this: \n\tclass "  
                            + name + "("
                            + bases[0].__name__+"[<YourType>], classType=<YourType>, superRoot="+ bases[0].__name__+"): ")
    
        
    
class AbstractGenericTypeValueSetterMetaClass(ABCMeta, GenericTypeValueSetterMetaClass):
    pass    
    

