#!/usr/bin/env python3

import enum


class Support(enum.IntEnum):
    UNKNOWN = 0
    TESTED = 1
    EXPECTED = 2
    PARTIAL = 3
    TODO = 4
    NEVER = 5
