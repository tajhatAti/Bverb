"""plugins/shield.py - Link Shield ke main client er sathe jure dey (linkguard.py te asol kaj)"""
import linkguard


def attach(hub_, client):
    linkguard.attach(hub_, client)
