"""
Helper functions which constructs blaze functions from dynd kernels.
"""

from __future__ import absolute_import, division, print_function

from dynd import nd, _lowlevel
import datashape

from ..function import ElementwiseBlazeFunc


def _make_sig(kern):
    dsret = datashape.dshape(str(nd.as_py(kern.proto).return_type))
    dslist = [datashape.dshape(str(x))
              for x in nd.as_py(kern.proto).param_types]
    return datashape.Function(*(dslist + [dsret]))


def blazefunc_from_dynd_property(tplist, propname, modname, name):
    """Converts a dynd property access into a Blaze ufunc.

    Parameters
    ----------
    tplist : list of dynd types
        A list of the types to use.
    propname : str
        The name of the property to access on the type.
    modname : str
        The module name to report in the ufunc's name
    name : str
        The ufunc's name.
    """
    # Get the list of type signatures
    kernlist = [_lowlevel.make_arrfunc_from_property(tp, propname,
                                                     'expr', 'default')
                for tp in tplist]
    siglist = [_make_sig(kern) for kern in kernlist]
    # Create the empty blaze function to start
    bf = ElementwiseBlazeFunc('blaze', name)
    # TODO: specify elementwise
    #bf.add_metadata({'elementwise': True})
    for (sig, kern) in zip(siglist, kernlist):
        bf.add_overload(sig, kern)
    return bf
