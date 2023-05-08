#!/use/bin/dev python
# -*- coding: utf-8 -*-
import sys
from AutoCython.AutoCython import AutoCython, AC_getopt_argv

__version__ = "1.3.3"

class MyModuleCall(sys.modules[__name__].__class__):
    # module call
    def __call__(self, *args, **kwargs):
        return AutoCython(*args, **kwargs)

sys.modules[__name__].__class__ = MyModuleCall

def main():
    """ main """
    ac = AutoCython(*AC_getopt_argv().geto())

    ac.compile()