
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
    
    self.rank = rank
    self.root = root
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
      super( Mf, self).__init__(lambda: Mf(rank-1, BaseClass,root=False ) )


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
      assert hasattr( BaseClass, extender ) and callable ( gettattr( BaseClass, extender ) ), 'The extender must be a callable method of BaseClass'

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
      assert hasattr( BaseClass, aggregator ) and callable ( gettattr( BaseClass, aggregator ) ), 'The aggregator must be a callable method of BaseClass'


  def all(self):

    assert self.aggregator != None
    oo = None
    if self.rank == 1:
      for k in self.keys():
        if oo == None:
          oo = self[k]
        else:
          oo = getattr( oo, self.aggregator )(self[k] )
    else:
      for k in self.keys():
        if oo == None:
          oo = self[k].all()
        else:
          oo = getattr( oo, self.aggregator )(self[k].all() )
    return oo

  def freeze(self,recursive=False):
    self.default_factory = None
    if recursive and self.rank > 1:
      for k in self.keys():
        self[k].freeze(recursive=True)

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
