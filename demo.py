"""

date: 18-11-7 下午8:10
"""
import base64
import os

print(base64.b64encode(os.urandom(48)).decode())