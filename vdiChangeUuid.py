#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
vdiChangeUuid.py - version and date, see below

Author :

* Goulag Parkinson - goulag dot parkinson at gmail.com

Licence : GPL v3 or any later version

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Goulag Parkinson (goulag.parkinson@gmail.com)'
__version__ = '0.1.1'
__last_modification__ = '2014.10.07'
__description__ = 'Change the internal UUID for VirtualBox VDI file'
__minimum_python_version__ = (2, 7, 6)
__maximum_python_version__ = (3, 4, 0)

import sys
from binascii import a2b_hex
from optparse import OptionParser
from struct import unpack
from array import array
from uuid import uuid4, UUID


def read_current_uuid(vdi_file, options):
    """Read the current UUID in the VDI file and return it as a uuid.UUID
    """
    try:
        vdi_file.seek(0x188)
        ba = unpack('16B', vdi_file.read(16))
        current_uuid_array = array('B', [ba[3], ba[2], ba[1], ba[0],
            ba[5],  ba[4], ba[7],  ba[6], ba[9],  ba[8],
            ba[10], ba[11], ba[12], ba[13], ba[14], ba[15]])
        to_hex = lambda x: "".join([hex(c)[2:].zfill(2) for c in x])
        current_uuid_hex = to_hex(current_uuid_array)
        current_uuid = UUID(current_uuid_hex)
        if options.verbose:
            print('INFO: Current UUID is %s' % str(current_uuid))
        return current_uuid
    except:
        print('CRITICAL: Unable to read the current UUID')
        return None


def write_new_uuid(vdi_file, options, str_uuid=None):
    if str_uuid:
        if options.debug:
            print('DEBUG : I have to take this uuid: %s' % str_uuid)
        try:
            uuid = UUID(str_uuid)
        except:
            print('FATAL: %s is not a valid UUID' % str_uuid)
            vdi_file.close()
            sys.exit()
    else:
        uuid = uuid4()
    if options.debug:
        print('DEBUG: Need to write %s in the file' % str(uuid))

    vdi_file.seek(0x188)
    uuid_hex = uuid.hex
    vdi_file.write(a2b_hex(uuid_hex[6:8]))
    vdi_file.write(a2b_hex(uuid_hex[4:6]))
    vdi_file.write(a2b_hex(uuid_hex[2:4]))
    vdi_file.write(a2b_hex(uuid_hex[0:2]))

    vdi_file.write(a2b_hex(uuid_hex[10:12]))
    vdi_file.write(a2b_hex(uuid_hex[8:10]))

    vdi_file.write(a2b_hex(uuid_hex[14:16]))
    vdi_file.write(a2b_hex(uuid_hex[12:14]))

    vdi_file.write(a2b_hex(uuid_hex[16:32]))

    if options.verbose:
        print('INFO: %s wrote in the file' % str(uuid))

    return uuid


def main(argv):
    """vdiChangeUuid, use it to change UUID of a VDI file
    """
    parser = OptionParser(
        usage="usage: %prog [options] file.vdi",
        description=__description__,
        version='%prog ' + __version__)

    parser.add_option('-D', '--debug', dest="debug",
                      action='store_true', help='display debug info',
                      default=False)
    parser.add_option('-v', '--verbose', dest="verbose",
                      action='store_true', help='display verbose info',
                      default=False)
    parser.add_option('-r', '--read', dest="read", action='store_true',
                      help='just read the current UUID', default=False)
    parser.add_option('-u', '--uuid', dest="uuid", action='store',
                      help='new UUID to store in file', default=None)

    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        parser.print_help()
        print('\n  %s' % __description__)
        sys.exit()

    vdi_filename = args[0]
    if not(vdi_filename.lower().endswith('.vdi')) and options.debug:
        print('DEBUG : file %s doesn\'t look like a vdi file (.vdi)' % vdi_filename)
    try:
        vdi_file = open(vdi_filename, 'r+b')
    except:
        print('FATAL : Error opening file %s' % vdi_filename)
        print('FATAL : %s' % sys.exc_info()[1])
        sys.exit()
    if options.read:
        current_uuid = read_current_uuid(vdi_file, options)
        print (str(current_uuid))
    else:
        write_new_uuid(vdi_file, options, options.uuid)
    vdi_file.close()


def test_python_version(enforce_maximum_version=False,
                        enforce_minimum_version=False):
    """Test the current python version and ensure it's looking ok
    """
    if sys.version_info[0:3] > __maximum_python_version__:
        if enforce_maximum_version:
            print('This program does not work with this version of Python (%d.%d.%d)' % sys.version_info[0:3])
            print('Please use Python version %d.%d.%d' % __maximum_python_version__)
            sys.exit()
        else:
            print('This program has not been tested with this version of Python (%d.%d.%d)' % sys.version_info[0:3])
            print('Should you encounter problems, please use Python version %d.%d.%d' % __maximum_python_version__)
    if sys.version_info[0:3] < __minimum_python_version__:
        if enforce_minimum_version:
            print('This program does not work with this version of Python (%d.%d.%d)' % sys.version_info[0:3])
            print('Please use Python version %d.%d.%d' % __maximum_python_version__)
            sys.exit()
        else:
            print('This program has not been tested with this version of Python (%d.%d.%d)' % sys.version_info[0:3])
            print('Should you encounter problems, please use Python version %d.%d.%d' % __maximum_python_version__)

if __name__ == "__main__":
    test_python_version()
    main(sys.argv[1:])
