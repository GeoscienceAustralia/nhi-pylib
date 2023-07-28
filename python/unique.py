from tendo import singleton
from tendo.singleton import SingleInstanceException

try:
    me = singleton.SingleInstance()
except SingleInstanceException:
    raise SingleInstanceException("Already running this process") from None
