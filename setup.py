#!/usr/bin/env python

import sys
sys.path = ['src'] + sys.path
import glob
import os
from distutils.core import setup
from SeriesFinale.lib import constants

def get_locale_files():
    files = glob.glob('locale/*/*/*.mo')
    file_list = []
    for file in files:
        destination_file_name = os.path.join(constants.DEFAULT_SYSTEM_APP_DIR, file)
        file_list.append((os.path.dirname(destination_file_name), [file]))
    return file_list

setup(name = constants.SF_NAME.lower(),
     version = constants.SF_VERSION,
     description = constants.SF_DESCRIPTION,
     author = 'Joaquim Rocha',
     author_email = 'jrocha@igalia.com',
     url = constants.SF_URL,
     license = 'GPL v3',
     packages = ['SeriesFinale', 'SeriesFinale.lib',
                 'jsonpickle'],
     package_dir = {'': 'src'},
     scripts = ['seriesfinale'],
     data_files = [('share/icons/hicolor/scalable/apps', ['data/seriesfinale.png']
                   ),
                   ('share/applications/hildon', ['data/seriesfinale.desktop']
                   ),
                   ] + get_locale_files()
     )
