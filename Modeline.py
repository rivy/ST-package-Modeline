## (emacs/sublime) -*- mode: python; coding: utf-8-unix; tab-width: 4;  st-trim_trailing_white_space_on_save: true; st-ensure_newline_at_eof_on_save: true; -*-

# Modeline parser
#
# Parses any '-*- ... -*-'-style (emacs) modeline within the first and/or last N lines of a file view,
# setting the detailed view variables.

# Emacs / VI(M) modeline info
# URLref: [Emacs - Specifying File Variables] http://www.gnu.org/software/emacs/manual/html_node/emacs/Specifying-File-Variables.html @@ http://webcitation.org/66xWWwjTt @@ http://archive.is/3kzGL
# URLref: [Emacs - Coding Systems] http://www.gnu.org/software/emacs/manual/html_node/emacs/Coding-Systems.html @@ http://webcitation.org/66xX3pMc1 @@ http://archive.is/pYoRF
# URLref: [Emacs - Specifying a File's Coding System] http://www.gnu.org/software/emacs/manual/html_node/emacs/Specify-Coding.html @@ http://webcitation.org/66xZ1nDWp @@ http://archive.is/vkbIL
# URLref: [VI - Modeline magic] http://vim.wikia.com/wiki/Modeline_magic @@ http://archive.is/Qrpxx @@ http://webcitation.org/6NIIqzbpF
# URLref: [Python and VIM] https://wiki.python.org/moin/Vim @@ http://archive.is/1ahCt

# URLref: [Sublime plugin settings] http://www.sublimetext.com/forum/viewtopic.php?f=6&t=9076#p36601 @@ http://archive.is/uc1Lw @@ http://

# ToDO: note that coding for python files under Windows needs to be utf-8-unix, utf-8-dos, or utf-8-mac (see the Windows BOM discussion @ http://www.python.org/dev/peps/pep-0263 @@ http://archive.is/CSE1q )

# NOTE: emacs/sublime type modelines are compatible and may be combined with vi(m) modelines
#   ... ex: ## (emacs/sublime) -*- mode: python; tab-width:4; -*- vim: set syntax=on tabstop=8 expandtab shiftwidth=4 softtabstop=4:


# Python v2/3 compatiblity
# URLref: [__future__ imports] http://python-future.org/imports.html @@ http://archive.is/yHfDA @@ http://webcitation.org/6NDj2zuHH
# URLref: [Should I import unicode_literals?] http://python-future.org/imports.html#unicode-literals
from __future__ import absolute_import, division, print_function, unicode_literals

###

PLUGIN_NAME = 'Modeline'
SETTINGS_FILENAME = PLUGIN_NAME + '.sublime-settings'

INIT_DELAY = 4000	# initialization delay (for ST2), in msec

MODELINE_RE = r'.*-\*-\s*(.+?)\s*-\*-.*'

DEFAULT_MODELINE_REGION = 'top'     # 'top', 'bottom', 'both'
DEFAULT_MODELINE_REGION_SIZE = 5 	# lines

###

import re
import os
import time

if __package__ == None:
	# for ST2: enable relative imports of python modules
	# URLref: [] http://docs.python.org/dev/reference/import.html @@ http://archive.is/5LETt
	# URLref: [] http://docs.python.org/2.6/tutorial/modules.html?highlight=__path__#packages-in-multiple-directories @@ http://archive.is/udQuv
	__package__ = __name__
	# NOTE: __path__ == an iterable of strings (if defined)
	if '__path__' not in globals(): __path__ = []
	__path__ = list( __path__ )
	__path__.append( '.' )

from .lib import common

#common.DEBUG = True

# enable logging of lib/logging module (if/when needed)
# common.DEBUG_LOGGING_MODULE = True
if common.DEBUG_LOGGING_MODULE:
	import logging as _logging
	log = _logging.getLogger( __package__ )
	log.setLevel( 1 )                       # [ 1, DEBUG, INFO, WARNING, ERROR, CRITICAL ]

from .lib import logging
log = logging.getLogger( __package__ )
if common.DEBUG:
	log.setLevel( logging.DEBUG )           # [ 1, STUDY/TRACE, DEBUG, INFO, NOTICE, DESIGN, WARNING, ERROR, CRITICAL ]
else:
	log.setLevel( logging.NOTICE )          # [ 1, STUDY/TRACE, DEBUG, INFO, NOTICE, DESIGN, WARNING, ERROR, CRITICAL ]

from .lib import sublime
import sublime_plugin

log.setLevel( logging.INFO )          # [ 1, STUDY/TRACE, DEBUG, INFO, NOTICE, DESIGN, WARNING, ERROR, CRITICAL ]

###

ST_V3 = 3000

###

def init ( ):
	log.debug( '.begin' )
	Preferences.load()
	render_templates() # instantiate any plugin templates
	ModelineWorker.begin_work()
	log.info( 'initialization completed' )

###

## see CursorRuler
## Prefenences is static to support add_on_change() #? true (is static needed for any reason?)

class Preferences:
	# class variables (static/shared)
	log = logging.getLogger( '.'.join(( __name__, 'Preferences' )) )
	log.debug( '.begin' )
	is_loaded = False
	settings_filename = SETTINGS_FILENAME
	settings = None
	## filename of user base preferences/settings changed in ST build 2174
	if int( sublime.version() ) >= 2174:
		settings_base_filename = 'Preferences.sublime-settings'
	else:
		settings_base_filename = 'Base File.sublime-settings'
	settings_base = None

	## namespace for loaded preferences
	class Var:
		pass
	var = Var()

	@classmethod
	def load ( cls, settings_filename=None ):
		cls.log.debug( '.begin' )

		cls.is_loaded = False

		if cls.settings_filename is not None:
			cls.log.info( '%sloading preferences', 're'*(cls.settings is not None) )
		#
		if settings_filename is not None:
			cls.settings_filename = settings_filename
			cls.settings = None

		if cls.settings is None:
			cls.settings = sublime.load_settings( cls.settings_filename )
		if cls.settings_base is None:
			cls.settings_base = sublime.load_settings( cls.settings_base_filename )

		key_prefix = os.path.splitext( os.path.basename( cls.settings_filename ) )[0].lower()

		# connect to preference change events
		event_key = 'on_change'
		cls.settings.clear_on_change( event_key )
		cls.settings.add_on_change( event_key, cls.load )
		cls.settings_base.clear_on_change( '-'.join(( key_prefix, event_key )) )
		cls.settings_base.add_on_change( '-'.join(( key_prefix, event_key )), cls.load )

		# load settings
		## load "base settings" from common user preferences
		## ex: cls.test_value = int( cls.settings_base.get( '.'.join(( key_prefix, 'test_value' )), -1 ) )

		## load plugin file settings
		cls.var.modeline_region = str( cls.settings.get( 'modeline_region', DEFAULT_MODELINE_REGION ) ).lower()
		cls.var.modeline_region_size = int( cls.settings.get( 'modeline_region_size', DEFAULT_MODELINE_REGION_SIZE ) )

		cls.log.debug( 'modeline_region = %s', cls.var.modeline_region )
		cls.log.debug( 'modeline_region_size = %d', cls.var.modeline_region_size )

		## load known modes from available syntax (*.tmLanguage) files
		cls.var.modes = {}
		for syntax_file in sublime.find_resources( '*.tmLanguage' ):
			name = os.path.splitext( os.path.basename( syntax_file ) )[0].lower()
			cls.var.modes[name] = syntax_file
			cls.log.trace( "%s [@ %s]", name, syntax_file )
		### load mode maps
		if cls.settings.has( 'mode_map_default' ):
			for modeline, syntax in cls.settings.get( 'mode_map_default' ).items():
				cls.var.modes[modeline] = cls.var.modes[syntax.lower()]
		if cls.settings.has( 'mode_map' ):
			for modeline, syntax in cls.settings.get( 'mode_map' ).items():
				cls.var.modes[modeline] = cls.var.modes[syntax.lower()]

		cls.is_loaded = True
		cls.log.debug( '.end' )
		return cls

###


def to_json_type ( v ):
	# log.debug( '.begin' )
	# from "https://github.com/SublimeText/Modelines/blob/master/sublime_modelines.py"
	""""Convert string value to proper JSON type.
	"""
	if v.lower() in ('true', 'false'):
		v = v[0].upper() + v[1:].lower()
	try:
		return eval(v, {}, {})
	except:
		raise ValueError("Could not convert to JSON type.")

###

def render_templates ():
	pass

###

class ModelineListener(sublime_plugin.EventListener):

	def __init__( self ):
		# minimal code here to speed ST startup
		# NOTE: for ST3+, object __init__'s happen before the full sublime API is available (aka, the initial API dormancy state)
		# setup class logging
		self.log = logging.getLogger( ".".join(( __name__, self.__class__.__name__ )) )
		self.log.debug( '.begin' )

	def on_activated( self, view ):
		# NOTE: ST2, on_activated() is triggered for all loaded views upon initial startup; ST3,
		self.log.debug( '.begin' )
		ModelineWorker.eval_view( view )

	def on_load( self, view ):
		self.log.debug( '.begin' )
		ModelineWorker.eval_view( view )

	def on_post_save( self, view ):
		self.log.debug( '.begin' )
		ModelineWorker.eval_view( view )

###

class ModelineWorker:
	log = logging.getLogger( '.'.join(( __name__, 'ModelineWorker' )) )
	log.debug( '.begin' )
	queue = {}

	@classmethod
	def begin_work ( cls ): ## ??: name not technically correct, items may already be queued for processing ... change to proceed, process_startup_queue, ...
		cls.log.debug( '.begin' )
		if len( cls.queue ) > 0:
			# queue'd work to do
			cls.eval_view( None ) 	# trigger view processing

	@classmethod
	def eval_view ( cls, view ):
		cls.log.debug( '.begin' )

		# queue view for processing
		if view is not None:
			key = str( view.id() )
			n = 1
			if key in cls.queue: n = cls.queue[key]['n'] + 1
			cls.queue[key] = { 'view': view, 'n': n }
			cls.log.debug( "cls.queue[%s][n] = %d", key, cls.queue[key]['n'] )

		if len( cls.queue ) == 0:
			cls.log.warning( "no views to parse (i.e., eval_view( None ) called with empty view queue)" )
			return

		# fully initialized?
		if not Preferences.is_loaded:
			# initialization not complete
			cls.log.debug( "view (id:%s) queued for later processing", str( view.id() ) )
			return

		while len( cls.queue ) > 0:
			(key, val) = cls.queue.popitem()
			cls.log.debug( "parsing view (id:%s)", key )
			view = val['view']
			# log.trace( "view.settings().get('syntax') = %s", view.settings().get('syntax') )
			modeline_match = cls.match_modeline( view )
			if modeline_match is not None:
				cls.eval_modeline( view, modeline_match )

	@classmethod
	def match_modeline ( cls, view ):
		cls.log.debug( '.begin' )
		# cls.log.trace( "view.settings().get('syntax') = %s", view.settings().get('syntax') )

		pref = Preferences.var

		# determine possible modeline locations within view

		## determine regions for evaluation
		regions = []
		if ( pref.modeline_region != 'bottom' ):
			# 'both' or 'top'
			region_end = view.text_point( pref.modeline_region_size, 0 )
			region = sublime.Region( 0, region_end )
			# log.design( 'top.region = %s', region )
			regions.append( region )
		if ( pref.modeline_region != 'top' ):
			# 'both' or 'bottom'
			eof_row = view.rowcol( view.size() )[0]
			region_start = view.text_point( eof_row - pref.modeline_region_size + 1, 0 )
			region = sublime.Region( region_start, view.size() )
			regions.append( region )
		## ToDO: ?? coalesce regions

		## determine lines for evaluation from region list
		## NOTE: lines are specified as character position pairs [eg, (start_pos, end_pos) ]
		lines = []
		for r in regions:
			lines.extend( view.lines(r) )
		cls.log.info( '[%s: %s] lines = %s', str(view.id()), view.file_name(), lines )

		# check for a modeline within designated line set

		for line in lines:
			# find modeline (via regexp match)
			m = re.match(MODELINE_RE, view.substr(line))
			if m:
				return m
		return None

	@classmethod
	def eval_modeline ( cls, view, modeline_match ):
		pref = Preferences.var

		modeline = modeline_match.group(1).lower() 	## ?? should lower() be used

		# Split into options
		for opt in modeline.split(';'):
			opts = re.match('\s*(st-|sublime-text-|sublime-|sublimetext-)?(.+):\s*(.+)\s*', opt)

			if opts:
				key, value = opts.group(2), opts.group(3)

				if opts.group(1):
					# log.study( "settings().set(%s, %s)" % (key, value) )
					view.settings().set(key, to_json_type(value))
				elif key == "coding":
					value = re.match('(?:.+-)?(unix|dos|mac)', value).group(1)
					if value == "dos":
						value = "windows"
					if value == "mac":
						value = "CR"
					view.set_line_endings(value)
				elif key == "indent-tabs-mode":
					if value == "nil" or value.strip == "0":
						view.settings().set('translate_tabs_to_spaces', True)
					else:
						view.settings().set('translate_tabs_to_spaces', False)
				elif key == "mode":
					if value in pref.modes:
						view.settings().set('syntax', pref.modes[value])
				elif key == "tab-width":
					view.settings().set('tab_size', int(value))
			else:
				# Not a 'key: value'-pair - assume it's a syntax-name
				if opt.strip() in pref.modes:
					view.settings().set('syntax', modes[opt.strip()])
		# EOFN

###

def plugin_loaded ( ):
	log.debug( '.begin' )
	# minimize initialization code here to speed ST startup
	# import sys
	# log.debug( "SublimeText version = '%s'", sublime.version() )
	# log.debug( "python version = %s", sys.version )
	# log.study( "cwd = %s", os.getcwd() )


	# # much of this is NOT available at ST startup; plugin_loaded() is executed when ST has finished startup/initialization
	# log.design( "__name__ = '%s'", __name__ )
	# log.design( "__package__ = '%s'", __package__ )
	# log.design( "package_name() = '%s'", sublime.package_name() )
	# log.design( "package_dir() = %s", sublime.package_dir() )
	# log.design( "package_path() = %s", sublime.package_path() )
	# log.design( "packages_dir() = %s", sublime.packages_dir() )
	# log.design( "packages_path() = %s", sublime.packages_path() )
	# log.design( "installed_package_path() = %s", sublime.installed_package_path() )
	# log.design( "installed_packages_dir() = %s", sublime.installed_packages_dir() )
	# log.design( "installed_packages_path() = %s", sublime.installed_packages_path() )
	# # NOTE: find_resources() only matches the _filename_ not the whole path of the available resources
	# # # log.design( "find_resources('*.tmLanguage') = %s", list( sublime.find_resources('*.tmLanguage') ) )
	# # # log.design( "find_resources('*.sublime-menu') = %s", list( sublime.find_resources('*.sublime-menu') ) )
	# # log.design( "find_package_resources('*.sublime-menu') = %s", list( sublime.find_package_resources('*.sublime-menu') ) )
	# # log.design( "find_package_resources('*.template') = %s", list( sublime.find_package_resources('*.template') ) )
	# r = sublime.load_resource( sublime.sublime_pathform ( os.path.join( sublime.package_dir(), 'Main.sublime-menu' ) ) )
	# log.design( "r[14] = %s", r.splitlines()[14] )
		# log.design( "find_resources_regex('.*sublime-menu') = %s", list( sublime.find_resources_regex('.*sublime-menu') ) )
		# log.design( "find_resources_regex('.*sublime-settings') = %s", list( sublime.find_resources_regex('.*sublime-settings') ) )
	# installed_package_path = sublime.installed_package_path()
	# # log.design( "installed_package_path = %s", installed_package_path )
	# if os.path.exists(installed_package_path):
	#     file_time_n = os.path.getmtime(installed_package_path)
	#     file_time = time.ctime(os.path.getmtime(installed_package_path))
	#     # log.debug( "installed_package_path_time = [%s] == %s", file_time_n, file_time )
	# main_menu_path_unpacked = os.path.join(sublime.packages_path(), sublime.package_name(), 'Main.sublime-menu')
	# if os.path.exists(main_menu_path_unpacked):
	#     file_time_n = os.path.getmtime(main_menu_path_unpacked)
	#     file_time = time.ctime(os.path.getmtime(main_menu_path_unpacked))
	#     # log.debug( "unpacked_time = [%s] == %s", file_time_n, file_time )
	# # if unpacked_file_time > package_time: erase file, open resource, modify, save as file
	# global pref
	# settings_base = sublime.load_base_settings()
	# settings = sublime.load_settings( SETTINGS_FILENAME )
	# pref = Preferences( settings, settings_base )
	# pref = Preferences( settings )
	# event_key = 'on_reload'
	# settings.clear_on_change( event_key )							# ToDO: ? needed for plugin reload, so that pref.load() isn't called multiple times
	# settings_base.clear_on_change( '-'.join(( PLUGIN_NAME, event_key )) )	# ToDO: ? needed for plugin reload, so that pref.load() isn't called multiple times
	# settings.add_on_change( 'test_on_change', test_on_change )
	# settings_base.add_on_change( '-'.join(( PLUGIN_NAME, event_key )), lambda:pref.load() )
	# log.design( "settings = %s", settings )

	# delay further initialization until ST UI is displayed/operating (minimizes perceived opening delay)
	delay = INIT_DELAY
	if ( int( sublime.version() ) >= ST_V3 ):
		# ST3+: plugin loading, initialization, and execution are processed on a seperate thread (no delay needed)
		delay = 0
	sublime.set_timeout( init, delay )


if sublime.version() and ( int( sublime.version() ) < ST_V3 ):
	# ST2: explicitly call the same initialization code as used by ST3
	log.info( '(ST2) call plugin_loaded() function' ) # .or. sys._getframe().f_code.co_name
	plugin_loaded()

###
