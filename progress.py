#!/usr/bin/env python3
#
# Copyright (c) 2018-2020 William Chanrico.
#
# This file is part of follower-gender-classification
# (see https://github.com/williamchanrico/follower-gender-classification).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys


def start_progress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()

    progress_x = 0


def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x


def end_progress():
    print("\n")
    sys.stdout.flush()
