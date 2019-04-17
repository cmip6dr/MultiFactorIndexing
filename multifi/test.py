
import zipfile
import multify

class Aggregate(object):
  def __init__(self,seed=None):
    if seed != None:
      self.sz = seed.sz
      self.nn = seed.nn
    else:
      self.sz = 0.
      self.nn = 0

  def __repr__(self):
    if isinstance( self, Aggregate ):
      return 'test.Aggregate instance: count=%s, size=%s' % (self.nn,self.sz)
    else:
      return 'test.Aggregate class' 

  def copy(self):
    return Aggregate( self )

  def add(self,x):
    if type(x) == type(self):
      self.sz += x.sz
      self.nn += x.nn
    else:
      self.sz += x
      self.nn += 1

  def join(self,other):
    oo = self.copy()
    oo.add( other )
    return oo

# '-rw-r----- 1 badc cmip5_research 1220170312 Apr 24  2011 output1/BCC/bcc-csm1-1/1pctCO2/day/ocean/day/r1i1p1/latest/tos/tos_day_bcc-csm1-1_1pctCO2_r1i1p1_01900101-01991231.nc'
class Test(object):
  def __init__(self):
    zip = zipfile.ZipFile( 'fileList_20150706.zip', 'r' )
    ii = zip.open( 'fileList_20150706.txt' )
    self.mf = multify.Mf( 3, Aggregate, extender='add', aggregator='join', indexKeys=[0,1,2] )

    ll = []
    for l in ii.readlines()[:50000]:
      l0 = l.decode('UTF-8').strip().split()
      sz = int( l0[4] )
      fn = l0[-1].split( '/' )[-1]
      if fn.find('historical') != -1 or True:
        bits = fn.split('_')
        if bits[0] == 'gridspec':
          bits = bits[1:]
        var = '%s.%s' % (bits[0],bits[1])
        model = bits[2]
        expt = bits[3]
        self.mf.Append( [var,model,expt], sz )

    print ( self.mf.all() )    
      

##t = Test()
    
