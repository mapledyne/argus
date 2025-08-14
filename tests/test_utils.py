"""Test utilities for the argus module."""


def close_file_handler():
    """Close the file handler to ensure JSON structure is completed.
    
    This is a test utility function that should only be used in tests.
    It ensures that the JSON file handler is properly closed so that
    the JSON structure is complete and can be parsed.
    """
    # Access the internal _file_handler through the module
    from argus.utils import _file_handler
    if _file_handler:
        _file_handler.close()
