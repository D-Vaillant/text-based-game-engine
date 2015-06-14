""" rooms.py:
        Implementation of Rooms for Game.
"""
__author__ = "David Vaillant"

class Room():
    """ Room class. """
    codes = {
        '#IDEN':'id',
        '#NAME':'name',
        '#DESC':'entry_desc',
        '#HOLD':'holding',
            }
        
    def __init__(self, r):
        d = lambda s: r[s] if s in r else ''
        self.links = [x for x in d('L')]
        
        self.name = d('NAME')
        self.id = d('IDEN')
        self.entry_desc = d('DESC')
        
        ##self.examine_desc = d('EX')
        ##self.reentry_desc = d('RE')
        self.holding = d('HOLD').split(' | ')
        if self.holding == ['']: self.holding = []
        
        if d('DATA'): self.data = []
        self.is_visited = False
                              
    def on_entry(self):
        """ Runs whenever a room is entered. """
        self.is_visited = True
        return self.entry_desc
        
    def on_examine(self):
        return self.examine_desc if self.examine_desc \
                                 else "There's not much to see here."
    
    def __str__(self):  
        string = ("Name: {0}\n"
                  "ID: {1}\n"
                  "Entry message: {2}\n"
                  "Items contained: [").format(self.name,
                                               self.id,
                                               self.entry_desc)        
        for x in self.holding:
            try:
                string += x.id + " "
            except AttributeError:
                try:
                    string += x + " "
                except TypeError:
                    string += "ERROR: ABNORMAL HOLDINGS"
        string += "] \n"
        
        return string  
        
    @staticmethod
    def room_processor(room_info_dict, room_link_dict = None):
        """ Takes a Room info dictionary and creates a Room class dictionary.

        If a link info dictionary is provided, runs each Room's
        link_processor method to set the attribute. """
        r = {}
        # Iterates through the dictionary's keys and creates a new Room using
        # the associated value (a Room info dictionary).
        for x in room_info_dict:
            r[x] = Room(room_info_dict[x])

        if room_link_dict: 
            for x in room_link_dict:
                try:
                    r[x].link_processor(room_link_dict[x])
                except KeyError:
                    print("Tried to set links of a room which doesn't exist.")
                    print("Relevant line: ", x)
        return r
   
