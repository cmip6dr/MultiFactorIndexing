"""packageConfig
-------------

Basic information about the package, used by setup.py to populate package metadata.
"""

import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__) )

__versionComment__ = "Version 00.01"
__version__ = "00.01"
__title__ = "Multi Factor Indexing"
__description__ = "Indexing items by multiple factors, creating a dictionary tree. Building on collections.defaultdict"
##__uri__ = "http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/{0}".format(__version__)
__uri__ = "https://github.com/cmip6dr/MultiFactorIndexing"
__author__ = "Martin Juckes"
__email__ = "martin.juckes@stfc.ac.uk"
__license__ = "BSD"
__copyright__ = "Copyright (c) 2015 Science & Technology Facilities Council (STFC)"

version = __version__
