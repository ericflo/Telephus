from telephus.cassandra.ttypes import *
from telephus.protocol import ManagedThriftRequest
import time

class CassandraClient(object):
    def __init__(self, manager, keyspace, quorum=1):
        self.manager = manager
        self.keyspace = keyspace
        self.quorum = quorum
        
    def _time(self):
        return int(time.time() * 1000)
    
    def _getparent(self, columnParentOrCF, super_column=None):
        if isinstance(columnParentOrCF, str):
            return ColumnParent(columnParentOrCF, super_column=super_column)
        else:
            return columnParentOrCF
        
    def _getpath(self, columnPathOrCF, col, super_column=None):
        if isinstance(columnPathOrCF, str):
            return ColumnPath(columnPathOrCF, super_column=super_column, column=col)
        else:
            return columnPathOrCF
    
    def get(self, key, columnPath, column=None, super_column=None, quorum=None):
        cp = self._getpath(columnPath, column, super_column)
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('get', self.keyspace, key, cp, quorum)
        return self.manager.pushRequest(req)
    
    def get_slice(self, key, columnParent, names=None, start='', finish='',
                  reverse=False, count=100, quorum=None, super_column=None):
        cp = self._getparent(columnParent, super_column)
        srange = SliceRange(start, finish, reverse, count)
        quorum = quorum or self.quorum
        pred = SlicePredicate(names, srange)
        req = ManagedThriftRequest('get_slice', self.keyspace, key, cp, pred,
                                   quorum)
        return self.manager.pushRequest(req)
    
    def multiget(self, keys, columnPath, column=None, super_column=None, quorum=None):
        cp = self._getpath(columnPath, column, super_column)
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('multiget', self.keyspace, keys, cp, quorum)
        return self.manager.pushRequest(req)
    
    def multiget_slice(self, keys, columnParent, names=None, start='', finish='',
                  reverse=False, count=100, quorum=None, super_column=None):
        cp = self._getparent(columnParent, super_column)
        srange = SliceRange(start, finish, reverse, count)
        quorum = quorum or self.quorum
        pred = SlicePredicate(names, srange)
        req = ManagedThriftRequest('multiget_slice', self.keyspace, keys, cp,
                                   pred, quorum)
        return self.manager.pushRequest(req)
    
    def get_count(self, key, columnParent, quorum=None):    
        cp = self._getparent(columnParent)
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('get_count', self.keyspace, key, cp,
                                   quorum)
        return self.manager.pushRequest(req)
    
    def get_key_range(self, start='', end='', limit=1000, quorum=None):
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('get_key_range', self.keyspace, start, end,
                                   limit, quorum)
        return self.manager.pushRequest(req)

    def insert(self, key, columnPath, value, column=None, super_column=None,
               timestamp=None, quorum=None):
        timestamp = timestamp or self._time()
        cp = self._getpath(columnPath, column, super_column)
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('insert', self.keyspace, key, cp, value,
                                   timestamp, quorum)
        return self.manager.pushRequest(req)

    def remove(self, key, columnPath, column=None, super_column=None, 
               timestamp=None, quorum=None):
        cp = self._getpath(columnPath, column, super_column)
        timestamp = timestamp or self._time()
        quorum = quorum or self.quorum
        req = ManagedThriftRequest('remove', self.keyspace, key, cp,
                                   timestamp, self.quorum)
        return self.manager.pushRequest(req)

    def batch_insert(self, key, columnFamily, mapping, quorum=None):
        first = mapping.keys()[0]
        if isinstance(mapping[first], dict):
            return self._batch_insert_super(key, columnFamily, mapping, quorum)
        else:
            return self._batch_insert_column(key, columnFamily, mapping, quorum)
        
    def _batch_insert_column(self, key, columnFamily, mapping, quorum=None):
        quorum = quorum or self.quorum
        cols = []
        for col,val in mapping.iteritems():
            cols.append(ColumnOrSuperColumn(column=Column(col, val, self._time())))
        cfmap = {columnFamily: cols}
        req = ManagedThriftRequest('batch_insert', self.keyspace, key, cfmap, quorum)
        return self.manager.pushRequest(req)
    
    def _batch_insert_super(self, key, columnFamily, mapping, quorum=None):
        quorum = quorum or self.quorum
        supers = []
        for name in mapping:
            cols = []
            for col,val in mapping[name].iteritems():
                cols.append(Column(col, val, self._time()))
            supers.append(ColumnOrSuperColumn(super_column=SuperColumn(name=name, columns=cols)))
        cfmap = {columnFamily: supers}
        req = ManagedThriftRequest('batch_insert', self.keyspace, key, cfmap, quorum)
        return self.manager.pushRequest(req)

    def get_string_property(self, name):
        req = ManagedThriftRequest('get_string_property', name)
        return self.manager.pushRequest(req)

    def get_string_list_property(self, name):
        req = ManagedThriftRequest('get_string_list_property', name)
        return self.manager.pushRequest(req)

    def describe_keyspace(self, keyspace):
        req = ManagedThriftRequest('describe_keyspace', keyspace)
        return self.manager.pushRequest(req)
