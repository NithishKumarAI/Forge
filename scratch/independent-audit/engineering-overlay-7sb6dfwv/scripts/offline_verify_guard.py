"""Test-process-only Python network/provider sentinel; no OS-wide firewall changes."""
import importlib.abc
import socket
import sys


def install():
    local={'127.0.0.1','localhost','::1',None,''}
    connect=socket.socket.connect;connect_ex=socket.socket.connect_ex;resolve=socket.getaddrinfo
    def destination(address):
        if isinstance(address,tuple) and address[0] not in local:raise PermissionError('External networking denied in offline verification')
    def guarded_connect(sock,address):destination(address);return connect(sock,address)
    def guarded_connect_ex(sock,address):destination(address);return connect_ex(sock,address)
    def guarded_resolve(host,*args,**kwargs):
        if host not in local:raise PermissionError('External DNS denied in offline verification')
        return resolve(host,*args,**kwargs)
    socket.socket.connect=guarded_connect;socket.socket.connect_ex=guarded_connect_ex;socket.getaddrinfo=guarded_resolve
    class BlockProvider(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname.startswith(('google','app.providers','scripts.authoring')):raise RuntimeError('Provider import forbidden in offline verification')
    sys.meta_path.insert(0,BlockProvider())
