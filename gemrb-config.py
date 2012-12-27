#!/usr/bin/env python
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

import sys
from modules import parser

if sys.version_info.major == 3:
	from modules import gui32 as gui
elif sys.version_info.major == 2 and sys.version_info.minor >= 7:
	from modules import gui27 as gui
else:
	print("You will need at least python 2.7 to run this program.")
	sys.exit()

source = parser.Source('GemRB.cfg.skel')

if not source: 
	print('Input file not found. Add GemRB.cfg.skel to directory.')

gui.GUI(source).main()
