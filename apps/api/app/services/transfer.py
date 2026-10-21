"""Transfer selection lives in the shared static assessment engine."""
from .assessment import start

def start_transfer(session,topic):
    return start(session,topic,"transfer")
