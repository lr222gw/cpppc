
from PyQt5.QtCore import Qt

def combine_alignment_flags(*args: Qt.AlignmentFlag) -> Qt.Alignment:
    """
    Combine multiple alignment flags to create a single alignment.
    Purpose is to avoid Pylance errors when bitwise combining flags...

    Args:
        *args (Qt.AlignmentFlag): The alignment flags to be combined.

    Returns:
        Qt.Alignment: The combined alignment flag.

    """
    result = Qt.Alignment()
    for arg in args:
        result |= arg
    return result    

