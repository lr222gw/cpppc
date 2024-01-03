import inspect
import textwrap


def terminate(msg:str):
    frame_info = inspect.stack()[1]    
    moduleLineInfoStr = _getModuleAndLineInfo(frame_info)    

    print("\n\n====================")
    print("PROGRAM TERMINATION!\n")
    print("Stack Trace:")
    print(textwrap.indent(_get_stack_from_frame()," "))

    print(str.format("\nTermination message: {}\n Error at: ",msg))    
    print(textwrap.indent(moduleLineInfoStr,"  "))
    
    exit("Failed")


def _getModuleAndLineInfo(frame_info: inspect.FrameInfo) -> str:
    classModule = ""
    className   = ""
    funcName    = ""
    if 'self' in frame_info.frame.f_locals:
        classModule = frame_info.frame.f_locals['self'].__module__
        className   = frame_info.frame.f_locals['self'].__class__.__name__
        funcName   = frame_info.function
    lineError =     str.format("MODULE: {}:{}:{}\n", classModule, className, funcName)
    lineError +=    str.format("FILE:   {}:[{}]\n", frame_info.filename, frame_info.lineno)
    return lineError

def _get_stack_from_frame():
    stack_info = inspect.stack()[2:]
    stack_str = ""
    for frame_info in stack_info:
        stack_str += f"File: {frame_info.filename}:[{frame_info.lineno}], Function: {frame_info.function}\n"
    return stack_str