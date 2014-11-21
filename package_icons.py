##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of the HDF Compass Viewer. The full HDF Compass          #
# copyright notice, including terms governing use, modification, and         #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

"""
Program to embed PNG icon files in an importable Python module.

Syntax: python package_icons.py outfile.py file1.png [file2.png ...]

"""

import sys
import glob
import base64
import os.path as op

def chunker(seq, size):
    """ Return a generator which breaks *seq* in to *size*-length chunks.
    """
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def run(in_names, out_name):
    """ Main program.

    out_fname: Name of Python module to write.
    """

    dct = {}    # File name -> Base64 encoded content

    for fname in in_names:

        with open(fname, 'rb') as f:
            data = f.read()
            if data[0:8] != b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A":
                raise ValueError('"%s" is not a valid PNG file' % fname)
            bname = op.basename(fname)
            dct[bname] = base64.b64encode(data)

    with open(out_name, 'w') as f:

        f.write('import base64\n\n')
        for name, string in sorted(dct.iteritems()):
            string = [('"%s"'%s) for s in chunker(string, 75)]
            string = "\n".join(string)
            name = op.basename(name).split('.')[0]
            f.write(
"""\
def %s():
    return base64.b64decode(
%s)

""" % (name, string))


if __name__ == '__main__':
    if len(sys.argv) < 3:   # program name, infile, outfile
        sys.stderr.write(__doc__)
        sys.exit(1)

    in_names = sys.argv[2:]
    out_name = sys.argv[1]

    run(in_names, out_name)
