import eng.data as data
import eng.error as error

_MAPS = {}
_TILESETS = {}

def init(fn):
   root = data.getTreeRoot(fn, "Resources main")

   mapsNode = root.getChild("maps")
   for mapNode in mapsNode.getChildren("map"):
      _MAPS[mapNode.getAttr("id", data.D_STRING)] = mapNode.getAttr("file", data.D_FILENAME)

   tilesetsNode = root.getChild("tilesets")
   for tilesetNode in tilesetsNode.getChildren("tileset"):
      _TILESETS[tilesetNode.getAttr("id", data.D_STRING)] = tilesetNode.getAttr("file", data.D_FILENAME)

def getMapFn(mapId):
   try:
      return _MAPS[mapId]
   except KeyError:
      raise error.DevError("No map with id \"{}\"".format(mapId))

def getTilesetFn(tsId):
   try:
      return _TILESETS[tsId]
   except KeyError:
      raise error.DevError("No tileset with id \"{}\"".format(tsId))
