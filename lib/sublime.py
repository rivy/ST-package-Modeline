# (emacs/sublime) -*- mode:python; coding: utf-8-unix; tab-width: 4;  st-trim_trailing_white_space_on_save: true; st-ensure_newline_at_eof_on_save: true; -*-

# sublime version compatiblity layer
# * backports ST3 API to ST2

from __future__ import absolute_import, division, print_function, unicode_literals
# from __future__ import absolute_import, division, print_function

# print( "__name__ = %s" % __name__ )
# print( "__package__ = %s" % __package__ )

# import sublime
from sublime import *

import inspect
import os

from . import logging
log = logging.getLogger( __name__ )

# log.study( "__name__ = %s", __name__ )
# log.study( "__package__ = %s", __package__ )
# log.study( "cwd = %s", os.getcwd() )

# determine current Sublime Text version
# NOTE: # early versions of ST3 might return ''
# _st_version_n = int(sublime.version()) if sublime.version() else 3000
_st_version_n = int( version() ) if version() else 3000
# log.debug( "_st_version_n = %s", _st_version_n )

# initial CWD (needed for ST2 to correctly determine package information)
_package_cwd = os.getcwd()
# log.debug( "_package_cwd = %s", _package_cwd )

###

_version = version
def version ( ):
    # log.debug( ".begin" )
    v = _version()
    if not v: v = '3000'
    assert v == str( _st_version_n )
    return v


def version_n ( ):
    # log.debug( ".begin" )
    v_n = int( version() )
    assert v_n == _st_version_n
    return v_n

###

def package_name ( ):
    # log.debug( ".begin" )
    st_vn = version_n()
    if st_vn >= 3000:
        name = __name__.split('.')[0]
    else:
        # ST2
        name = os.path.basename( _package_cwd )
    return name

_package_name = package_name()

###

def sublime_pathform ( path ):
    # log.debug( ".begin" )
    # ST (as of build 2181) requires *NIX/MSYS style paths (using '/') in several areas (eg, for the 'syntax' view setting)
    return path.replace( "\\", "/" )

###

# NOTES
# dir == ST/*NIX-form relative directories
# path == OS-form absolute paths

def installed_packages_dir ( ):
    # log.debug( ".begin" )
    return 'Installed Packages'

_installed_packages_path = installed_packages_path
def installed_packages_path ( ):
    # log.debug( ".begin" )
    return _installed_packages_path()


def installed_package_path ( package_name=_package_name ):
    return os.path.join( installed_packages_path(), package_name+'.sublime-package' )


def packages_dir ( ):
    # log.debug( ".begin" )
    return 'Packages'

_packages_path = packages_path
def packages_path ( ):
    # log.debug( ".begin" )
    return _packages_path()


def package_dir ( package_name=_package_name ):
    # log.debug( ".begin" )
    return sublime_pathform( os.path.join( packages_dir(), package_name ) )


def package_path ( package_name=_package_name ):
    # log.debug( ".begin" )
    return os.path.join( packages_path(), package_name )

###

try: _find_resources = find_resources
except NameError:
    _find_resources = None

def find_resources ( fnmatch_pattern ):
    # log.debug( ".begin" )
    import fnmatch
    import os
    # if hasattr(sublime, 'find_resources'):
    if _find_resources is not None:
        for f in _find_resources( fnmatch_pattern ):
            yield f
    else:
        # ST2
        for root, dirs, files in os.walk( _packages_path() ):
            for f in files:
                if fnmatch.fnmatch( f, fnmatch_pattern ):
                    langfile = os.path.relpath( os.path.join(root, f), _packages_path() )
                    yield sublime_pathform( os.path.join( packages_dir(), langfile ) )

###

_DEFAULT_MAX_CACHE_TIME = 600   # 600 sec == 10 min
_resource_cache = []
_resource_cache_timestamp = 0

def _get_resources ( max_cache_time=_DEFAULT_MAX_CACHE_TIME ):
    # log.debug( ".begin" )
    import time
    now = time.time()
    global _resource_cache
    global _resource_cache_timestamp
    if (( now - _resource_cache_timestamp ) > max_cache_time ):
        # info( "cache expired; re-reading all resources" )
        _resource_cache = list ( find_resources( '*' ) )
        _resource_cache_timestamp = now
    # log.notice( "len(_resource_cache) = %d", len(_resource_cache) )
    return _resource_cache


def find_package_resources ( fnmatch_pattern, package_name=_package_name, max_cache_time=_DEFAULT_MAX_CACHE_TIME ):
    # log.debug( ".begin" )
    import fnmatch, os
    files = _get_resources( max_cache_time )
    prefix = sublime_pathform( os.path.join( packages_dir(), package_name ) )
    # log.info( "prefix = '%s'", prefix )
    for f in files:
        if f.startswith( prefix ):
            if fnmatch.fnmatch( f, fnmatch_pattern ):
                yield f


def find_resources_regex ( regex_pattern, max_cache_time=_DEFAULT_MAX_CACHE_TIME ):
    # log.debug( ".begin" )
    import re
    files = _get_resources( max_cache_time )
    regex = re.compile( regex_pattern )
    for f in files:
        if regex.match(f):
            yield f

###

try: _load_resource = load_resource
except NameError:
    _load_resource = None

def load_resource ( path ):
    # log.debug( ".begin" )
    if _load_resource is not None:
        return _load_resource( path )
    else:
        # ST2
        resource_path = os.path.join( os.path.dirname( _installed_packages_path() ), path )
        with open( resource_path ) as file:
            resource = file.read()
        return resource

try: _load_binary_resource = load_binary_resource
except NameError:
    _load_resource = None

def load_binary_resource ( path ):
    # log.debug( ".begin" )
    if _load_binary_resource is not None:
        return _load_binary_resource( path )
    else:
        # ST2
        resource_path = os.path.join( os.path.dirname( _installed_packages_path() ), path )
        with open( resource_path, mode='rb' ) as file:
            resource = file.read()
        return resource


def resource_abstract_path ( path ):
    # path of file or .sublime-package which holds the resource content
    # log.debug( ".begin" )
    pass

def is_resource_accessible ( path ):
    # log.debug( ".begin" )
    pass

###

def load_base_settings ( ):
    st_vn = version_n()
    if st_vn >= 2174:
        settings_base = load_settings('Preferences.sublime-settings')
    else:
        settings_base = load_settings('Base File.sublime-settings')
    return settings_base
