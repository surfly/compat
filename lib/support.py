#!/usr/bin/env python3

import enum


class Support(enum.IntEnum):
    UNKNOWN = 0
    SUPPORTED = 1
    EXPECTED = 2
    TODO = 3
    NEVER = 4
