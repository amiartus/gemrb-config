#!/bin/python3.2

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
from gi.repository import Gtk

class GUI(Gtk.Window):

	def __init__(self, source):
		window = Gtk.Window()
		window.connect("delete_event", self.delete)
		window.set_title("GemRB Config")
		window.set_border_width(10)
		window.set_default_size(800, 400)

		mainbox = Gtk.VBox()
		window.add(mainbox)

		# Create a new notebook, place the tabs
		notebook = Gtk.Notebook()
		notebook.set_tab_pos(Gtk.PositionType.LEFT)
		mainbox.pack_start(notebook, True, True, padding = 0)

		for section in source.sections:		
			vbox = Gtk.VBox()
			vbox.set_border_width(0)
			vbox.set_tooltip_text("\n".join(section.description))

			scrolled_window = Gtk.ScrolledWindow()
			scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)

			vbox.pack_start(scrolled_window, True, True, padding = 0)

			section_vbox = Gtk.VBox()
			scrolled_window.add_with_viewport(section_vbox)
			
			for i, option in enumerate(section.options):
				frame = Gtk.Frame()
				frame.set_label(option.name)
				frame.set_tooltip_text("\n".join(option.description))
				
				if option.type == 'Radiobutton' or option.type == 'Boolean':
					self.makeRadioblock(frame, option)

				elif option.type == "String":
					self.makeStringblock(frame, option)

				elif option.type == "Path":
					self.makePathblock(frame, option)

				elif option.type == "Slidebutton":
					self.makeSlideblock(frame, option)
				
				else:
					print('WARNING: Missing button for type:', option.type)

				section_vbox.pack_start(frame, False, False, padding = 10)
				
			label = Gtk.Label(section.name)
			notebook.append_page(vbox, label)
		
		commit = Gtk.Button("Commit")
		commit.set_size_request(100, -1)
		commit.set_halign(2)
		commit.connect("clicked", self.handler_Commit_clicked, source)
		mainbox.pack_start(commit, False, False, padding = 0)

		notebook.set_current_page(0)

		window.show_all()
	
	def makeRadioblock(self, parent, option):
		radiobox = Gtk.HBox(spacing = 6)
		parent.add(radiobox)
		button = []
		
		for j, choice in enumerate(option.choices):
			if j == 0:
				button.append(Gtk.RadioButton.new_with_label_from_widget(None, choice if option.type == 'Radiobutton' else 'No'))
			else:
				button.append(Gtk.RadioButton.new_with_label_from_widget(button[j-1], choice if option.type == 'Radiobutton' else 'Yes'))

			button[j].connect("toggled", self.handler_Radiobutton_toggled, j, option)
			radiobox.pack_start(button[j], False, False, 0)
		
		button[option.choices.index(option.default_value)].set_active(True)

	def handler_Radiobutton_toggled(self, button, index, option):
		if button.get_active(): 
			option.current = option.choices[index]
			print ("Button", index, "from group", button.get_parent().get_parent().get_label(), "was turned", button.get_active(), "currentval is", option.current)

	def makePathblock(self, parent, option):
		hbox = Gtk.HBox(spacing = 6)
		parent.add(hbox)
		
		textfield = Gtk.Entry()
		textfield.connect("focus_out_event", self.handler_Textbox_FocusOut, option)	
		textfield.set_text(option.default_value)
		hbox.pack_start(textfield, True, True, 0)
	
		button = Gtk.Button("Choose Folder")
		button.set_size_request(10, -1)
		button.connect("clicked", self.handler_FileChooserDialog_clicked, option)
		hbox.pack_start(button, False, False, 0)	

	def makeStringblock(self, parent, option):
		textfield = Gtk.Entry()
		textfield.connect("focus_out_event", self.handler_Textbox_FocusOut, option)
		textfield.set_text(option.default_value)
		parent.add(textfield)
	
	def handler_Textbox_FocusOut(self, button, __WHAT_IS_THIS__, option):
		print('Textfield is set to:', button.get_text())
		option.current = button.get_text()

	def handler_FileChooserDialog_clicked(self, button, option):
		dialog = Gtk.FileChooserDialog("Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
		dialog.set_default_size(200, 200)

		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			print ("Select clicked")
			print ("Folder selected: " + dialog.get_filename())
			option.current = dialog.get_filename()
			button.get_parent().get_children()[0].set_text(dialog.get_filename())
		elif response == Gtk.ResponseType.CANCEL:
			print ("Cancel clicked")

		dialog.destroy()

	def makeSlideblock(self, parent, option):
		slider = Gtk.HScale.new_with_range(int(option.choices[0]), int(option.choices[1]), 1)
		slider.connect("button_release_event", self.handler_Slider_Release, option)
		slider.set_value(int(option.default_value))
		parent.add(slider)

	def handler_Slider_Release(self, button, __WHAT_IS_THIS__, option):
		print("Button released, new val is:", int(button.get_value()))
		option.current = str(int(button.get_value()))
	
	def handler_Commit_clicked(self, button, source):
		outputfile = open('gemrb.cfg','w')
		outputfile.write(source.dump())
		outputfile.close()		

	def delete(self, widget, event = None):
		Gtk.main_quit()
		return True			

class Source:

	def __init__(self, fname):
		self.section_start = []
		self.sections = []

		if not os.path.exists(fname):
			print('Invalid Source File.')
			os._exit(1)

		self.filename = fname
		self.buff  = [line.strip() for line in open(fname, 'r')]

		for i, string in enumerate(self.buff):
			if string.find('#@') == 0:
				self.section_start.append(i)
		
		for i, item in enumerate(self.section_start):
			if item == self.section_start[-1]:
				self.sections.append(Section(self.buff[item:self.buff.__len__()]))
			else:
				self.sections.append(Section(self.buff[item:self.section_start[i+1] - 1]))

	def dump(self):
		buffer = ''
		for section in self.sections:
			buffer += section.dump()
		return buffer

class Section:

	def __init__(self, buff):	
		self.description = []
		self.option_start = []
		self.options = []

		self.name = buff[0].lstrip('#@ ')
		
		if buff.__len__() == 1: return

		for i, string in enumerate(buff):
			
			if string.find('#+') == 0:
				self.option_start.append(i)
		
		for i, string in enumerate(buff[1:self.option_start[0]]):
			if not string: continue
			if string[0] == '#': self.description.append(string.lstrip('# '))
		
		for i, item in enumerate(self.option_start):
			if item == self.option_start[-1]:
				self.options.append(Option(buff[item:buff.__len__()]))
			else:
				self.options.append(Option(buff[item:self.option_start[i+1] - 1]))
	
	def dump(self):
		buffer = '# ' + self.name + '\n' 
		if self.description: buffer += '# ' + '\n# '.join(self.description) + '\n'

		for option in self.options:
			buffer += option.dump()

		return buffer

	def print(self):
		print('\n' + self.name)
		print('\n'.join(self.description))
		print(self.option_start)
		for i in self.options:
			i.print()			

class Option:

	def __init__(self, buff):
		self.description = []
		self.choices = []

		self.name = buff[0].lstrip('#+ ')

		self.words = buff[1].split()
		
		self.option_string = self.words[1]
		self.type = self.words[2]

		if self.type == 'Boolean':
			self.choices = ['0', '1']
		elif self.type == 'Radiobutton' or self.type == 'Slidebutton':
			self.choices = self.words[3:self.words.__len__()]

		for i, string in enumerate(buff[2:(buff.__len__()-1)]):
			if not string: continue
			if string[0] == '#': self.description.append(string.lstrip('# '))

		self.default_value = buff[-1].split('=',1)[-1]
		self.current = self.default_value

	def dump(self):
		buffer = '# ' + self.name + '\n'
		if self.description: buffer += '# ' + '\n# '.join(self.description) + '\n'
		
		if self.option_string: buffer += self.option_string + '=' + self.current + '\n\n'

		return buffer

	def print(self):
		print('\n' + self.name)
		print('\n'.join(self.description))
		print(self.type)
		print(self.choices)
		print(self.default_value)

def main():
	Gtk.main()
	return 0

a = Source('./GemRB.cfg.skel')

for i in a.sections:
	i.print()

if __name__ == "__main__":
	GUI(a)
	main()
