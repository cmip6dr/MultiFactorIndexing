
import collections


class KeyError(object):
  pass

class Mf(collections.defaultdict):
  """Wrapper for collections.defaultdict which enables multi-factor indexing through a ranked defaultdict.
     The integer rank defines the number of independent factors which can be used in the indexing.

     Example:
     -------

     itemList = [['Joe','Bloggs',12],['Jane','Bloggs',15],['Mike','Jones',14]]
     rank = 3
     myIndex = Mf(2,set)

     ## create a dictionary, indexed by age and surname.
     for x in itemList:
       myIndex[x[2]][x[1]].add(x)

  """
  def __init__(self,rank,BaseClass,factors=None,indexKeys=None,mapping=None,name=None,root=True,aggregator=None,extender=None):
    """The class is initialised with a rank (positive integer) and base class (python class object);
    """
    
    self.BaseClass = BaseClass 
    self.name = name
    self.rank = rank
    self.root = root
    self.tkeys = TupleKeys(self)
    assert type(rank) == type(1),'rank (first argument) must be an integer: %s' % rank
    assert rank > 0,'rank (first argument) must be positive: %s' % rank

    self.indexKeys = indexKeys
    if indexKeys != None:
      assert len( indexKeys ) == rank, 'If present, indexKeys must have length equal to rank=%s: %s' % (rank,len(indexKeys))
      if factors != None:
        print ('WARNING: argument factors will be ignored: indexKeys takes precedence')
      if mapping != None:
        print ('WARNING: argument mapping will be ignored: indexKeys takes precedence')
    self.factors = factors
    if mapping == None and factors != None and indexKeys == None:
        assert len( factors ) == rank, 'If mapping is not present, factors, if used, must have length equal to rank=%s: %s' % (rank,len(factors))
    if factors != None and indexKeys == None:
        assert all( [callable(f) for f in factors] ), 'factors argument must provide list of callable elements'
    self.mapping = mapping
    if mapping != None and indexKeys == None:
      if factors == None:
        print ('WARNING: argument mapping will be ignored: factors argument not present')
      else:
        assert len( mapping ) == rank, 'If used, mapping must have length equal to rank=%s: %s' % (rank,len(mapping))
        assert all( [len[m]==2 for m in mapping] ), 'mapping argument must provide list of elements of length 2'
        assert all( [ all( [type(x) == type(1) for x in m] )  for m in mapping] ), 'mapping argument must provide list of elements of length 2'
        assert all( [m[0] < len(factors) and m[0] >= 0] ), 'mapping items first elements must be valid indices of the factors list: %s' % mapping
    
    if rank == 1:
      super( Mf, self).__init__(BaseClass)
    elif rank > 1:
      super( Mf, self).__init__(lambda: Mf(rank-1, BaseClass,root=False,aggregator=aggregator, extender=extender ) )


    self.extender = extender
    if extender == None:

      ## use 'add' to extend sets
      if hasattr( BaseClass, 'add' ) and callable( BaseClass.add ):
        self.extender = 'add'

      ## use append to extend lists
      elif hasattr( BaseClass, 'append' ) and callable( BaseClass.append ):
        self.extender = 'append'
      ## use __add__ to extend lists
      elif hasattr( BaseClass, '__add__' ) and callable( BaseClass.__add__ ):
        self.extender = '__add__'
    else:
      assert hasattr( BaseClass, extender ) and callable ( getattr( BaseClass, extender ) ), 'The extender must be a callable method of BaseClass'

    assert self.extender != None, 'Extender not found. If baseClass does not have a callable attribute add, append or __add__, the extender must be explicitly specified as an argument'

    self.aggregator = aggregator
    if aggregator == None:

      ## use 'union' to aggregate sets
      if hasattr( BaseClass, 'union' ) and callable( BaseClass.union ):
        self.aggregator = 'union'

      ## use __add__ to aggregate lists and integers
      elif hasattr( BaseClass, '__add__' ) and callable( BaseClass.__add__ ):
        self.aggregator = '__add__'
    else:
      assert hasattr( BaseClass, aggregator ) and callable ( getattr( BaseClass, aggregator ) ), 'The aggregator must be a callable method of BaseClass'


  def squash(self,lev,name=None):
    if name == None:
       name = '%s [minus %s]' % (self.name,lev)
    new = Mf( self.rank-1,self.BaseClass,name=name,aggregator=self.aggregator,extender=self.extender)
    for t in self.tkeys:
      t2 = list( t[:] )
      t2.pop(lev-1)
      new.Append( t2, self.Tget( t ) )

    return new
      
  def levelKeys(self,lev):
    ss = set()
    if lev == 1:
      for k in self.keys():
        ss = ss.union( set( self[k].keys() ) )
    else:
      for k in self.keys():
        ss = ss.union( set( self[k].levelKeys(lev-1) ) )
    return ss
      
  def all(self,filter=None):

    assert self.aggregator != None
    oo = None
    if self.rank == 1:
      for k in self.keys():
        if filter == None or (self.rank not in filter) or (k in filter[self.rank]):
          if oo == None:
            oo = self[k]
          else:
            oo = getattr( oo, self.aggregator )(self[k] )
    else:
      for k in self.keys():
        if filter == None or (self.rank not in filter) or (k in filter[self.rank]):
          ook = self[k].all( filter=filter )
          if ook != None:
            if oo == None:
              oo = ook
            else:
              oo = getattr( oo, self.aggregator )( ook )
    return oo

  def freeze(self,recursive=False):
    self.default_factory = None
    if recursive and self.rank > 1:
      for k in self.keys():
        self[k].freeze(recursive=True)

  def ReMap( self, levmap):
    assert len(levmap) == self.rank
    assert len(levmap) == len(set(levmap))
    assert min(levmap) == 0 and max(levmap) == self.rank-1


## to do reorder in place:
## need to ensure that tkey does not start returning new keys ... should be OK since copy of keys is taken at start of iteration.
## need to ensure that new keys dont overwrite old ... can use a prefix, kk --> (unique,kk), where "unique" is not in set of kk[0] values.
##
    ##for t in self.tkey;

  def Tget( self, keys):
    if self.rank == 1:
      return self[keys[0]]
    else:
      return self[keys.pop(0)].Tget( keys )

  def Append( self, keys, item ):
    """At item to the multi-index, indexed on a tuple of keys.
       Keys must be a list or tuple of length equalt to the rank.
       For rank 2, this call is equivalent to:

        self[keys[0]][keys[1]] = item
    """

    if self.rank == 1:
      getattr( self[keys[0]], self.extender )( item )
    else:
      self[keys.pop(0)].Append( keys, item )

  def AutoIndex(self,ll):
    """Index a list using the index keys or factors defined by the instantiation of this object.
    If index keys are defined, each item of the list will be added as:
      self[item[k1]][item[k2]].... = item

    If factors are defined with no mapping:

      self[ f1(item) ][ f2(item) ]... = item

    If mappings are defined, a tuple F is obtained by applying the factors to an item and then
      self[ F[m1[0]][m1[1]] ][ F[m2[0]][m2[1]] ].... = item

    """

    assert self.root, 'Auto-indexing is only supported at the root of a multilevel index'
    for item in ll:
      if self.indexKeys != None:
        keys = [item[k] for k in self.indexKeys]
      else:
        keys = [f(item) for f in self.factors ]
        if self.mapping != None:
          new = []
          for m in self.mapping:
            if m[1] == None:
              new.append( keys[m[0]] )
            else:
              new.append( keys[m[0]][m[1]] )
          keys = new
      self.Append( keys, item )

class TupleKeys(object):
  """The TupleKeys class provides an iterator over the multi-level structure of the 
     Mf class.
     --------------------
     Usage
     -----
     tk = TupleKeys(mf) # mf an instance of Mf
     for t in tk:
       print (t)

     The class is instantiated in Mf, as mf.tkey.
  """
  def __init__(self,mf):
    self.mf = mf
    self.rank = mf.rank

  def __iter__(self):
    self.keys = list(self.mf.keys())
    self.mf.__iter__()
    self.a = 0
    if self.rank > 1:
       self.mf[self.keys[self.a]].tkeys.__iter__()
    return self

  def __len__(self):
    if self.rank == 1:
      return len(self.mf.keys())
    else:
      l = 0
      for k in self.mf.keys():
        l += self.mf[k].tkeys.__len__()
      return l

  def __next__(self):
    if self.a < len(self.keys):
      x = self.keys[self.a]
      if self.rank == 1:
        self.a += 1
        return x
      else:
        try:
          x1 = self.mf[x].tkeys.__next__()
        except StopIteration:
          self.a += 1
          if self.a >= len(self.keys):
            raise
          x = self.keys[self.a]
          self.mf[x].tkeys.__iter__()
          x1 = self.mf[x].tkeys.__next__()
        if self.rank == 2:
          return [x,x1]
        else:
          return [x,] + x1
    else:
      raise StopIteration
