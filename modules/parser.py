# Ths a GUI for setting up a config file for GemRB.
# Copyright (C) 2012-2013  Adam Miartus
#
# This file is part of Gemrb-config.
#
# Gemrb-config is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gemrb-config is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gemrb-config.  If not, see <http://www.gnu.org/licenses/>.

import os

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
		
		if self.option_string: 
			if self.current == "none":
				buffer += '# '

			buffer += self.option_string + '=' + self.current + '\n\n'

		return buffer
