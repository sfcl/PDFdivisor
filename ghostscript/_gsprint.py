#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2010 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3)"
__version__ = "0.4.1"

from ctypes import *
import sys
import os

from ghostscript._errors import *

MAX_STRING_LENGTH = 65535

class Revision(Structure):
    _fields_ = [
        ("product", c_char_p),
        ("copyright", c_char_p),
        ("revision", c_long),
        ("revisiondate", c_long)
        ]

gs_main_instance = c_void_p
display_callback = c_void_p

class GhostscriptError(RuntimeError):
    def __init__(self, ecode):
         # :todo:
         RuntimeError.__init__(self, error2name(ecode))

def revision():
    """
    Get version numbers and strings.

    This is safe to call at any time.
    You should call this first to make sure that the correct version
    of the Ghostscript is being used.

    Returns a Revision instance
    """
    revision = Revision()
    rc = libgs.gsapi_revision(pointer(revision), sizeof(revision))
    if rc:
        raise ArgumentError("Revision structure size is incorrect, "
                            "requires %s bytes" % rc)
    return revision

def new_instance(): # display_callback=None):
    """
    Create a new instance of Ghostscript
    
    This instance is passed to most other API functions.
    """
    # :todo: The caller_handle will be provided to callback functions.
    display_callback=None
    instance = gs_main_instance()
    rc = libgs.gsapi_new_instance(pointer(instance), display_callback)
#    if rc != 0:
#        raise GhostscriptError(rc)
    return instance

def delete_instance(instance):
    """
    Destroy an instance of Ghostscript
    
    Before you call this, Ghostscript must have finished.
    If Ghostscript has been initialised, you must call exit()
    before delete_instance()
    """
    return libgs.gsapi_delete_instance(instance)


c_stdstream_call_t = CFUNCTYPE(c_int, gs_main_instance, POINTER(c_char), c_int)

def _wrap_stdin(infp):
    """
    Wrap a filehandle into a C function to be used as `stdin` callback
    for ``set_stdio``. The filehandle has to support the readline() method.
    """
    
    def _wrap(instance, dest, count):
        try:
            data = infp.readline(count)
        except:
            count = -1
        else:
            if not data:
                count = 0
            else:
                count = len(data)
                memmove(dest, c_char_p(data), count)
        return count

    return c_stdstream_call_t(_wrap)

def _wrap_stdout(outfp):
    """
    Wrap a filehandle into a C function to be used as `stdout` or
    `stderr` callback for ``set_stdio``. The filehandle has to support the
    write() and flush() methods.
    """

    def _wrap(instance, str, count):
        outfp.write(str[:count])
        outfp.flush()
        return count

    return c_stdstream_call_t(_wrap)

_wrap_stderr = _wrap_stdout


def set_stdio(instance, stdin, stdout, stderr):
    """
    Set the callback functions for stdio.

    ``stdin``, ``stdout`` and ``stderr`` have to be ``ctypes``
    callback functions matching the ``_gsprint.c_stdstream_call_t``
    prototype. You may want to use _wrap_* to wrap file handles.

    Please note: Make sure you keep references to C function objects
    as long as they are used from C code. Otherwise they may be
    garbage collected, crashing your program when a callback is made

    The ``stdin`` callback function should return the number of
    characters read, `0` for EOF, or `-1` for error. The `stdout` and
    `stderr` callback functions should return the number of characters
    written.
    """
    rc = libgs.gsapi_set_stdio(instance, stdin, stdout, stderr)
    if rc not in (0, e_Quit, e_Info):
        raise GhostscriptError(rc)
    return rc


# :todo:  set_poll (instance, int(*poll_fn)(void *caller_handle));
# :todo:  set_display_callback(instance, callback):

def init_with_args(instance, argv):
    """
    Initialise the interpreter.

    1. If quit or EOF occur during init_with_args(), the return value
       will be e_Quit. This is not an error. You must call exit() and
       must not call any other functions.
       
    2. If usage info should be displayed, the return value will be
       e_Info which is not an error. Do not call exit().
       
    3. Under normal conditions this returns 0. You would then call one
       or more run_*() functions and then finish with exit()
    """
    ArgArray = c_char_p * len(argv)
    idx=0
    for arg in argv:
        argv[idx] = bytes(str(arg), 'utf-8')
        idx+=1
    c_argv = ArgArray(*argv) 
    rc = libgs.gsapi_init_with_args(instance, len(argv), c_argv)

    #if rc not in (0, e_Quit, e_Info):
    #    raise GhostscriptError(rc)

    return rc

def exit(instance):
    """
    Exit the interpreter
    
    This must be called on shutdown if init_with_args() has been
    called, and just before delete_instance()
    """
    rc = libgs.gsapi_exit(instance)
    #if rc != 0:
    #    raise GhostscriptError(rc)
    return rc


def run_string_begin(instance, user_errors=False):
    exit_code = c_int()
    rc = libgs.gsapi_run_string_begin(instance, c_int(user_errors),
                                      pointer(exit_code))
    if rc != 0:
        raise GhostscriptError(rc)
    return exit_code.value

def run_string_continue(instance, str, user_errors=False):
    exit_code = c_int()
    rc = libgs.gsapi_run_string_continue(
        instance, c_char_p(str), c_int(len(str)),
        c_int(user_errors), pointer(exit_code))
    if rc != e_NeedInput and rc != 0:
        raise GhostscriptError(rc)
    return exit_code.value

def run_string_end(instance, user_errors=False):
    exit_code = c_int()
    rc = libgs.gsapi_run_string_end(instance, c_int(user_errors),
                                    pointer(exit_code))
    if rc != 0:
        raise GhostscriptError(rc)
    return exit_code.value

def run_string_with_length(*args, **kw):
    raise NotImpelmentedError('Use run_string() instead')


def run_string(instance, str, user_errors=False):
    exit_code = c_int()
    rc = libgs.gsapi_run_string_with_length(
        instance, c_char_p(str), c_int(len(str)),
        c_int(user_errors), pointer(exit_code))
    if rc != 0:
        raise GhostscriptError(rc)
    return exit_code.value


def run_file(instance, filename, user_errors=False):
    exit_code = c_int()
    rc = libgs.gsapi_run_file(instance, c_char_p(filename), 
                              c_int(user_errors), pointer(exit_code))
    if rc != 0:
        raise GhostscriptError(rc)
    return exit_code.value


def set_visual_tracer(I):
    raise NotImplementedError

def __win32_finddll():
    #str1 ='C:\Python34\gs\lib\gsdll32.dll'
    # цель сделать доступными dll библиотеки imagemagic и gs из каталога программы
    # когда данные библиотеки не устаовлены
    try:
        approot = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        approot = os.path.dirname(os.path.abspath(sys.argv[0]))

    # import logging
    #
    # # create logger with 'spam_application'
    # logger = logging.getLogger('spam_application')
    # logger.setLevel(logging.DEBUG)
    # # create file handler which logs even debug messages
    # fh = logging.FileHandler('e:\\spam.log')
    # fh.setLevel(logging.DEBUG)
    #
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    #
    # # add the handlers to the logger
    # logger.addHandler(fh)


    file_name = os.path.abspath(sys.argv[0]).split(os.sep)[-1]
    ext = file_name.split('.')[-1]
    if ext == 'exe':
        approot = approot.split(os.sep)[:-2]
        approot = '\\'.join(approot)
        lib_dll = approot + '\\lib\\gsdll32.dll'
    else:
        approot = approot.split('\\')[:-1]
        approot = '\\'.join(approot)
        lib_dll = approot + '\\lib\\gsdll32.dll'

    #logger.info(lib_dll)
    #print('dll',lib_dll)
    return lib_dll


if sys.platform == 'win32':
    libgs = __win32_finddll()
    #print('libgs=', libgs)
    if not libgs:
        raise RuntimeError('Can not find Ghostscript DLL in registry')
    libgs = windll.LoadLibrary(libgs)
else:
    try:
        libgs = cdll.LoadLibrary("libgs.so")
    except OSError:
        # shared object file not found
        import ctypes.util
        libgs = ctypes.util.find_library('gs')
        if not libgs:
            raise RuntimeError('Can not find Ghostscript library (libgs)')
        libgs = cdll.LoadLibrary(libgs)

del __win32_finddll
