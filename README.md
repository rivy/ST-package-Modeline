# Modeline for Sublime Text

Parse Emacs-like modelines, setting per-buffer/local settings for Sublime Text 2 and/or 3.


## Installing

Installation via [Package Control](http://wbond.net/sublime_packages/package_control) is the recommended method.

Add

	"repositories":
	[
		"https://raw.github.com/rivy/ST-channel/master/repository.json"
	],

to the Package Control User configuration file (at "Preferences / Package Settings / Package Control / Settings - User").


## Usage

Somewhere within the first or last `N` lines (default == 5) of a file, add a line matching the following:

	-*- key: value; key2: value2 -*-

or

	-*- syntax -*-

Supported settings are '`mode`', '`tab-width`', '`indent-tabs-mode`', '`coding`', and '`sublime-*`.

Specifying '`sublime-`' (or '`st-`') allows changing Sublime Text preferences for that view. For
example, specifying '`st-trim_automatic_white_space: false`' disables automatic whitespace trimming.

The values for '`mode`' are the root filename of the .tmLanaguge file. Most of
the time these are obvious and match the syntax name but not all the time. For
example the 'Graphviz (DOT)' syntax is simply 'dot'. To find out the correct
value you can run this command in the console (ctrl+\`) when the syntax you want is in
use:

	view.settings().get('syntax')
	# u'Packages/Graphviz/DOT.tmLanguage' or u'Packages/Graphviz/DOT.sublime-syntax'
	# =>> 'DOT' is the mode value

If you want to use the same mode line settings with an emacs user you might need
to set up mappings from the emacs names to the sublime syntax names. To do this
look at the `mode_map` key in the settings file (which you can open via the
menu at "Preferences / Package Settings / Modeline / Settings - Default"). As an example this
package ships with a mapping from "Bash" (emacs) to "Shell-Unix-Generic" (sublime).

If you want to replace the default mode map, you can overwrite the `mode_map_default` key.


## Alternatives

* [Emacs-like Sublime Modeline](https://github.com/kvs/STEmacsModelines)
	* the original prototype for this addon
* [Vim-style modelines](https://github.com/SublimeText/Modelines)
<!--(missing):* [More Emacs-style hacks](http://software.clapper.org/ST2EmacsMiscellanea/)-->

## Meta

Re-written by [Roy Ivy III](https://github.com/rivy).

Originally created by [Kenneth Vestergaard](https://github.com/kvs).

Patches contributed by [Ash Berlin](https://github.com/ashb).

Released under the MIT License: http://www.opensource.org/licenses/mit-license.php .
