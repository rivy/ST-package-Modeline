# (emacs/sublime) -*- mode:python; coding: utf-8-unix; tab-width: 4;  st-trim_trailing_white_space_on_save: true; st-ensure_newline_at_eof_on_save: true; -*-

### lib.logging
# enhance python logging with NOTICE and TESTING levels

from __future__ import absolute_import, division, print_function, unicode_literals

_DEBUG = True

# print( "__name__ = %s" % __name__ )
# print( "__package__ = %s" % __package__ )
_root_package_name = __name__.split('.')[0]

from logging import *
log = getLogger( __name__ )

# DEFAULT_LOG_FORMAT = '%(name)s:%(funcName)s():@%(lineno)s:%(asctime)s:%(levelname)s: %(message)s'
# DEFAULT_LOG_FORMAT = '%(asctime)s:%(name)s:@%(lineno)s:%(funcName)s():%(levelname)s: %(message)s'
DEFAULT_LOG_FORMAT = _root_package_name+': %(message)s'

DEFAULT_LOG_DEBUG_FORMAT = '%(asctime)s:%(name)s:@%(lineno)s:%(funcName)s():%(levelname)s: %(message)s'
DEFAULT_LOG_INFO_FORMAT = _root_package_name+': %(levelname)s: %(message)s'
DEFAULT_LOG_NOTICE_FORMAT = _root_package_name+': %(message)s'
DEFAULT_LOG_WARNING_FORMAT = '%(name)s:%(funcName)s():%(levelname)s: %(message)s'

## define new levels
STUDY = DEBUG - 1
TRACE = DEBUG - 1
NOTICE = INFO + 1
DESIGN = NOTICE + 1

# setup default parent package logging
_log_package = getLogger( _root_package_name )
#_log_package.handlers = []   # PORT: not documented in 'logging', but needed to stop duplicate handlers on module reloads; ? future portability issue; enable of if submodule reloading is implemented

from . import common

# if 'DEBUG' not in globals() or not DEBUG:
if not common.DEBUG:
	_handler = StreamHandler()
	_handler.setFormatter( Formatter( DEFAULT_LOG_FORMAT ) )
	_log_package.addHandler( _handler )
else:
	# LevelRangeFilter
	import sys
	try: _MAX_INT = sys.maxint
	except AttributeError: _MAX_INT = sys.maxsize

	class LevelRangeFilter ( Filter ):
		def __init__ ( self, min=0, max=_MAX_INT ):
			self.min = min
			self.max = max
		def filter ( self, record ):
			if record.levelno < self.min: return False
			if record.levelno > self.max: return False
			return True

	_handler = StreamHandler()
	_handler.addFilter( LevelRangeFilter(max=DEBUG) )
	_handler.setFormatter( Formatter( DEFAULT_LOG_DEBUG_FORMAT ) )
	_log_package.addHandler( _handler )
	#
	_handler = StreamHandler()
	_handler.addFilter( LevelRangeFilter(min=DEBUG+1, max=NOTICE-1) )
	_handler.setFormatter( Formatter( DEFAULT_LOG_INFO_FORMAT ) )
	_log_package.addHandler( _handler )
	#
	_handler = StreamHandler()
	_handler.addFilter( LevelRangeFilter(min=NOTICE, max=NOTICE) )
	_handler.setFormatter( Formatter( DEFAULT_LOG_NOTICE_FORMAT ) )
	_log_package.addHandler( _handler )
	#
	_handler = StreamHandler()
	_handler.addFilter( LevelRangeFilter(min=NOTICE+1) )
	_handler.setFormatter( Formatter( DEFAULT_LOG_WARNING_FORMAT ) )
	_log_package.addHandler( _handler )

log.debug( "Finished default Logger setup for %s", _root_package_name )

# ToDO: add LevelRangeFilter(), create (0, DEBUG], (DEBUG, NOTICE], (NOTICE, +inf] ranges with specific output formats
#   ... LevelRangeFilter(logging.Filter).init(min=0, max=sys.maxint)

# add trace point logging (for msg==None) to usual logging levels
# URLref: http://stackoverflow.com/a/16955098/43774
# NOTE: sys._getframe() may alternatively be used for inspect.stack()[][]

## modify DEBUG logging level
def _log_debug ( self, message=None, *args, **kws ):
	if self.isEnabledFor( DEBUG ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( DEBUG, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( DEBUG, message, *args, **kws )

Logger.debug = _log_debug
log.debug( "logging.debug() modified" )

## modify INFO logging level
def _log_info ( self, message=None, *args, **kws ):
	if self.isEnabledFor( INFO ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( INFO, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( INFO, message, *args, **kws )

Logger.info = _log_info
log.debug( "logging.info() modified" )

## modify WARNING logging level
def _log_warning ( self, message=None, *args, **kws ):
	if self.isEnabledFor( WARNING ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( WARNING, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( WARNING, message, *args, **kws )

Logger.warning = _log_warning
log.debug( "logging.warning() modified" )

## modify ERROR logging level
def _log_error ( self, message=None, *args, **kws ):
	if self.isEnabledFor( ERROR ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( ERROR, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( ERROR, message, *args, **kws )

Logger.error = _log_error
log.debug( "logging.error() modified" )

## modify CRITICAL logging level
def _log_critical ( self, message=None, *args, **kws ):
	if self.isEnabledFor( CRITICAL ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( CRITICAL, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( CRITICAL, message, *args, **kws )

Logger.critical = _log_critical
log.debug( "logging.critical() modified" )


# setup additional logging levels
# URLref: http://stackoverflow.com/a/16955098/43774

## add STUDY logging level
# STUDY = DEBUG - 1
addLevelName( STUDY, 'STUDY' )

def _log_study ( self, message=None, *args, **kws ):
	if self.isEnabledFor( STUDY ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( STUDY, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( STUDY, message, *args, **kws )

Logger.study = _log_study
log.debug( "logging.study() added" )

## add TRACE logging level
# TRACE = DEBUG - 1
addLevelName( TRACE, 'TRACE' )

def _log_trace ( self, message=None, *args, **kws ):
	if self.isEnabledFor( TRACE ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( TRACE, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( TRACE, message, *args, **kws )

Logger.trace = _log_trace
log.debug( "logging.trace() added" )

## add NOTICE logging level
# NOTICE = INFO + 1
addLevelName( NOTICE, 'NOTICE' )

def _log_notice ( self, message=None, *args, **kws ):
	if self.isEnabledFor( NOTICE ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( NOTICE, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( NOTICE, message, *args, **kws )

Logger.notice = _log_notice
log.debug( "logging.notice() added" )

## add DESIGN logging level
# DESIGN = NOTICE + 1
addLevelName( DESIGN, 'DESIGN' )

def _log_design ( self, message=None, *args, **kws ):
	if self.isEnabledFor( DESIGN ):
		import inspect
		if  message is None:
			message = "%s()" % inspect.stack()[1][0].f_code.co_name
		# _log() used instead of log() to avoid introducing another frame level for funcName, lineno purposes
		self._log( DESIGN, message, args, **kws ) 	# _log() takes *args as args ## NOTE: NOT self.log( DESIGN, message, *args, **kws )

Logger.design = _log_design
log.debug( "logging.design() added" )


log.study( "__name__ = %s", __name__ )
log.study( "__package__ = %s", __package__ )
log.study( "_root_package_name = %s", _root_package_name )
