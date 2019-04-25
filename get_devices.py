#!/usr/bin/env python3
import openmv
import re

dev = openmv.OpenMV()
dev.connect()
print('Board Info: {!r}'.format(dev.arch_id))
print('OpenMV Version:', dev.fw_version)
dev.disconnect()
