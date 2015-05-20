import os

import pygame

from . import globs
from . import settings
from . import data
from . import tileset
from . import error
from . import error_handling
from . import script_engine

####### TODO
#pockets can currently only have one id associated with them
#ideally they could have more, so for instance both ITEMS and MEDECINE could go in one pocket

class Item():
    """
    Represents a single item.

    Note quantity is dealt with by the bag, not the item.
    """
    
    def __init__(self, itemId):
        """
        Create the item from the id string.

        itemId - the id of the item.
        """

        #find the correct item node
        self.root = data.getTreeRoot(globs.ITEMS, "Items global")
        for item in self.root.getChildren("item"):
            if item.getAttr("id", data.D_STRING) == itemId:
                self.itemNode = item
                break
        else:
            raise ValueError
        

        #store the data from the node
        self.pocketId = self.itemNode.getAttr("pocket", data.D_STRING)
        self.name = self.itemNode.getAttr("name", data.D_STRING)
        self.itemId = self.itemNode.getAttr("id", data.D_STRING)
        self.price = self.itemNode.getAttr("price", data.D_INT)
        self.description = self.itemNode.getAttr("description", data.D_STRING)
        self.inBattle = self.itemNode.getAttr("inbattle", data.D_INT)
        self.outBattle = self.itemNode.getAttr("outbattle", data.D_INT)
        self.special = self.itemNode.getAttr("special", data.D_INT)

    def getImage(self):
        """Get the item's icon image."""

        #open the item icons "tileset"
        fn = os.path.join(settings.path, "data", self.root.getAttr("tileset", data.D_STRING))
        tsRoot = data.getTreeRoot(fn, self.root.ditto_fn)

        #work out the filename to use, and open the image
        #TODO - move the icon's path to the item's node and load it from there
        name = "item%i.png" % self.itemNode.getAttr("index", data.D_INT)
        fn = os.path.join(settings.path, "data", tsRoot.getAttr("folder", data.D_STRING), name)
        im = data.getImage(fn)

        #return the image
        return im

class Bag(script_engine.ScriptableObject):
    """The bag class."""
    
    def __init__(self):
        """Create the bag."""
        script_engine.ScriptableObject.__init__(self)

        #initialise an empty pockets dict
        self.pockets = {}

    def add(self, item, number=1):
        """
        Add an item to the bag.

        Adds it to the appropriate pocket, creating the pocket if it doesn't already exist.

        item - the item to add.
        number - the quantity to add
        """

        #if the bag doesn't have the pocket required, then add it
        if not item.pocketId in self.pockets:
            self.pockets[item.pocketId] = Pocket(item.pocketId)

        #add the item to the correct pocket
        self.pockets[item.pocketId].add(item, number)
                
    def remove(self, item, n):
        #remove the item from the bag

        # if there are more than one more than the amount being removed, simply reduce the number of items
        if item.amount >= n + 1:
            item.amount -= n
            return "decreased"
        else:
            # actually remove the item from the bag
            for pocket in self.bag:
                pocketNum = self.bag.index(pocket)
                if item in pocket:
                    itemNum = pocket.index(item)
                    del self.bag[pocketNum][itemNum]
                    return "deleted"

    def getPocket(self, pocketId):
        """
        Return the pocket corresponding to the pocket id.

        Creates an empty pocket if the pocket doesn't yet exist.

        pocketId - the id of the pocket to get.
        """
        
        #if we have that pocket, return it
        #else return an empty pocket
        try:
            return self.pockets[pocketId]
        except KeyError:
            self.pockets[pocketId] = Pocket(pocketId)
            return self.pockets[pocketId]

    def item_index(self, pocket, id):
        for i in pocket:
            if i.id == id:
                return pocket.index(i)
        else:
            print("item not in bag!")

    def check_got(self, item, pocket):
        # check whether the specified item is in the pocket
        for i in pocket:
            if i.name == item.name:
                return True
        else:
            return False

    def command_add(self, item, number):
      self.add(item, number)

class Pocket():
    """A single pocket."""
    
    def __init__(self, pocketId):
        """
        Create the pocket.

        pocketId - the id string of the pocket.
        """

        #store the pocket id
        self.pocketId = pocketId

        #initialise a blank list of the items,
        #and dict of the amounts
        self.items = [] #must be list to preserve order. Maybe look at OrderedDict?
        self.amounts = {}

    def add(self, item, number=1):
        """
        Add a quantity of an item to the pocket.

        Note does not check that the item is actually meant for this pocket.

        item - the item to add.
        number - the quantity to add.
        """

        #if we already have some of the item, add more
        #else, add the item to our list for the first time
        try:
            self.amounts[item.itemId] += number
        except KeyError:
            self.items.append(item)
            self.amounts[item.itemId] = number

    def remove(self, item, number=1):
        """
        Remove some number of an item from the pocket.

        Will raise an exception if the item isn't in the pocket.
        However won't care if there aren't as enough to remove. (Just removes all)

        item - the item to remove.
        number - the quantity to remove.
        """

        #decrease our amounts as needed
        self.amounts[item.itemId] -= number

        #if we've gotten down to 0 (or below) then remove the item completely
        if self.amounts[item.itemId] <= 0:
            del self.amounts[item.itemId]
            self.items.remove(item)        

    def getQuantity(self, item):
        """
        Find out how many of an item we have.

        item - the item to count
        """

        #see if we have any of the item, else return 0
        try:
            return self.amounts[item.itemId]
        except KeyError:
            return 0

    def __len__(self):
        """Find out how many different items we have."""
        
        return len(self.items)

    def __getitem__(self, i):
        """Get an item by index."""
        
        return self.items[i]
