import sublime, sublime_plugin
import urllib
import urllib2
import threading
from functools import partial
import os

class UpdateCiteulikeThread(threading.Thread):
	def __init__(self, command, username, timeout=5):
		self.command = command
		self.username = username
		self.timeout = timeout
		self.result = None
		threading.Thread.__init__(self)

	def run(self):
		try:
			request = urllib2.Request('http://www.citeulike.org/bibtex/user/%s' % self.username, headers={"User-Agent": "SublimeUpdateCiteULikeBib"})
			httpFile = urllib2.urlopen(request, timeout=self.timeout)
			self.result = httpFile.read()
			sublime.set_timeout(partial(self.command.downloadComplete, self.result), 0)
			return
		except (urllib2.HTTPError) as (e):
			err = '%s: HTTP error %s contacting CiteULike' % (__name__, str(e.code))
		except (urllib2.URLError) as (e):
			err = '%s: URL error %s contacting CiteULike' % (__name__, str(e.reason))
		sublime.error_message(err)
		self.result = False

class UpdateCiteulikeCommand(sublime_plugin.ApplicationCommand):

	def run(self):
		s = sublime.load_settings("Preferences.sublime-settings")
		username = s.get("CiteULike_username", None)
		if not username:
			sublime.active_window().show_quick_panel(["No username set!"], self.noAction)
			return

		sublime.active_window().active_view().set_status("UpdateCiteULike", "Downloading CiteULike references")
		thread = UpdateCiteulikeThread(self, username)
		thread.start()

	def downloadComplete(self, data):
		#sublime.active_window().show_quick_panel(["BibTex file updated!"], self.noAction)
		self.downloadedBytes = data
		sublime.active_window().active_view().set_status("UpdateCiteULike", "CiteULike references downloaded")
		sublime.active_window().show_input_panel("Save BibTex file to:", "references.bib", self.saveToFile, self.noAction, self.noAction)

	def saveToFile(self, filename):
		if sublime.active_window().active_view().file_name():
			filename = os.path.join(os.path.dirname(sublime.active_window().active_view().file_name()), filename)

		with open(filename, 'w') as f:
			f.write(self.downloadedBytes)
		sublime.active_window().active_view().set_status("UpdateCiteULike", "CiteULike references saved to file: %s" % filename)

	def noAction(self, value):
		pass