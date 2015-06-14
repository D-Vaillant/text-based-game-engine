"""
Project name: Architect

game.py:
        The engine for the command-line based game. 
        Some vocabulary needs to be clarified, many things need to be
    implemented. I'll document the individual modules here.

Blueprint:
        A domain specific language.
        
        I didn't want to define a new class for each room but different
    instances of classes can only differ semantically; changing Things
    required syntactic commands. Thus: I created a small system of commands
    which could be taken by an interpreter function which would then
    execute the commands.
        More information about the structure of Blueprint can be found in
    documentation/blueprint_library.txt.

Room:
        Container class for the rooms that the PC enters.

        Also contains the room_reader function which takes a Room info dict
    (see File_Processor) to create a Room class dict, one of the input
    parameters for the Game class. 

Thing:
        Container class for the objects that the PC encounters. Come in two
    varieties, props and items. Props are static and cannot be moved
    once placed (generally in a room) while items can be placed and
    removed from an Inventory.

        Also contains the object_reader function which takes a Thing info dict
    and creates a Thing class dict, one of the input parameters for the
    Game class.
    
Action:
        Contains information about player actions. 

Inventory:
        Container class for the PC's inventory. Contains items which 
    can be used from the inventory menu.

File_Processor:
        Only used when initializing the Game; reads a text file
    and translates it into two different dictionaries: a Room info dict
    and a Thing info dict. These info dicts are used by the Room and
    Thing classes and encode all the information about the game.
"""

from rooms import Room
from actions import Action
from object_source import Inventory, Thing
from file_management import File_Processor
import re

# Verbose option.
V = True

class Game():
    cardinals = {'w':0, 's':1, 'n':2, 'e':3}
    special_actions = ['take']
    blueprint_keywords = '[&!\-\+@#]'
    ERROR = {
        "exe_pass": "Invalid command.",
        "act_item_not_found": "It's not clear what thing " + 
                              "you're talking about.",
        "act_not_for_item": "That item cannot be used that way.",
        "act_using_rooms": "You can't do that with an entire room.",
        "act_already_holding": "You've already got one of those.",
        "act_taking_prop": "It doesn't seem like you could carry that.",
        "room_no_room_found": "WARNING: Incorrect room in Blueprint."
        }
    ACT_MSGS = {
        "Input < 2":"What do you want to do that to?",
        "0 < Max:":"You need to do that with something.",
        "Input > 0":"That doesn't make sense."
        }
    GAME_MSGS = {
        "beginning": "Welcome to the demo!",
        "quit": "Game closing."
        }
        
    #alias = {'_':loc, '^': }
    
#---------------------------- Initialization ---------------------------------
    def __init__(self, rdata, tdata, adata, mdata):
        self.isCLI = False 
        
        self.rooms = Room.room_processor(rdata)
        self.things = Thing.thing_processor(tdata)
        self.thing_names = {t.alias:t.id for t in self.things.values()}
        self.actions = Action.action_processor(adata)
        
        self._populate()
        
        # For eventual implementation of meta-data entry.
        """
        try: self.loc = self.mdata["firstRoom"]
        except KeyError: raise KeyError("Initial room either unspecified "+
                                        "or missing.")
        self.inventory = Inventory(ownedObjs) if mdata["ownedObjs"] \
                                              else Inventory()
        """
        
        self.loc = self.rooms["initial"]
        self.inventory = Inventory()
        self.setting_output = ''
        self.action_output = ''
        
    def _populate(self):
        for room in self.rooms.values():
            try:
                ##if V: print([t for t in room.holding])
                room.holding = [self.things[t_id] for t_id in room.holding]
            except KeyError:
                raise KeyError("Room holding non-existent thing.")
                
        ## Implementation of inventory populating.
        ## 
        ##
        return
        
    def _meta_processor(self, raw_mdata):
        return
        
#------------------------------ Utility Functions ----------------------------

    def _getThing(self, user_input):
        raise NotImplementedError

#-------------------------------- User Prompt --------------------------------

    def prompt_exe(self, prompt):
        ''' Takes player input and passes the corresponding command to the
            corresponding player command function. '''
            
        # Turns string inputs into arrays of strings.
        i = prompt.lower().split() if prompt != '' else ''
        
        # Does nothing if empty command is entered.
        if i == []: i = ''
        if len(i) < 1: return

        # Call _move if a movement command is entered.
        if i[0] in self.cardinals.keys():
            self._move(i)
        elif i[0] in ['west', 'south', 'north', 'east']:
            self._move(i[0][0])

        # Inventory call.
        elif i[0] in ["inv", "i"]:
            self._inv("open")
            
        # Call _act if an action is entered.
        elif i[0] in self.actions or self.special_actions:
            if V: print("Treating ", i[0], " as an action.")
            self._act(i)
        
        # System calls. ? calls help.
        elif i[0] == '?':
            self._help(i[1:])
            
        # Deprecated right now since Quit is handled by the GUI.
        elif i[0] == 'quit' or i[0] == 'q':
            self._puts(self.GAME_MSGS["quit"])
        
        # Puts an error message if an unrecognised command is entered.
        else:
            self._puts(self.ERROR["exe_pass"])
            
        if V: print()
        return        
            
    def _help(self, object):
        """ Puts help messages. """
        if object:
            pass
        else:
            self._puts("Movement: north, south, east, west")
            self._puts("Actions: " + ', '.join(self.actions))
        return
            
    ''' Classes of player commands: Moving, acting, and menu. '''

    def _move(self, direction):
        """ Attempts to change self.loc in response to movement commands. """
        # Transforms letters to Room.links array index (0-3).
        translated_direction = self.cardinals[direction[0][0]]
        
        try:
            self.loc = self.rooms[self.loc.links[translated_direction]]
        except KeyError:
            self._puts('I can\'t go that way.')
            return
        #self._room_update()
            
    # Act: Takes a command.
    # Deprecated by new action system.
    """
    def act(self, command):
        ''' Action function. '''
        tmp = ' '.join(command[1:])

        # If no object specified.
        if tmp == '':
            if command[0] == "examine":
                self._puts(self.loc.on_examine())
                #self._puts(Thing.thing_printer([self.things[x] for x in self.loc.holding]))
            else: 
                self._puts(self.ERROR["act_item_not_found"])
        # Examining.
        elif command[0] == "examine":
            if tmp == "room":
                self._puts(self.loc.on_examine())
                #self._puts(Thing.thing_printer([self.things[x] for x in self.loc.holding]))
            elif tmp in self.loc.holding or tmp in self.inventory.holding:
                self._puts(self.things[tmp].examine_desc)
            else: self._puts(self.ERROR["act_item_not_found"])
        # Taking.
        elif command[0] == "take":
            if tmp == "room":
                self._puts(self.ERROR["act_using_rooms"])
            elif tmp in self.loc.holding:
                if self._alias(tmp).isProp:
                    self._puts(self.ERROR["act_taking_prop"])
                else:
                    self.inventory.add_item(tmp)
                    self.loc.holding.remove(tmp)
                    self._puts("Picked up the " + tmp + ".")
            elif tmp in self.inventory.holding:
                self._puts(self.ERROR["act_already_holding"])
            else:
                self._puts(self.ERROR["act_item_not_found"])
        # Other actions.
        else:
            if tmp == "room":
                self._puts(self.ERROR["act_using_rooms"])
            elif tmp in self.loc.holding or tmp in self.inventory.holding:
                try:
                    for x in self.things[tmp].action_dict[command[0]]:
                        self.blueprint_main(x)
                except KeyError:
                    self._puts(self.ERROR["act_not_for_item"])
            else:
                self._puts(self.ERROR["act_item_not_found"])
        return
    """
    
    def _act(self, command):
        """ Does actiony stuff. Don't ask me! """
        if V: print("Running action prompt.")
       
        # Parses input as [action, specifics*].
        action = command[0]
        specifics = ' '.join(command[1:])
        
        # Hard coding of some actions like take, examine.
        ## Could theoretically be rolled into the Action class as well.
        if action in self.special_actions:
            if V: print("Special action being run.")
            
            self._special_act(action, specifics)
                    
        # User-specified actions.
        else:
            if V: print("Ordinary action being run.")
            # Turns action names into Action instances.
            action = self.actions[action]
            
            # Transforms specifics into either an error message string
            # or an array of Thing names.
            specifics = action.parse_string(specifics)
            
            
            # If parse_string returns a #F: prefixed string, put
            # an error message.
            if specifics and specifics[:2] == "#F:":
                self._puts(ACT_MSGS[specifics[2:]])
            
            # Turns the parsed string into (hopefully) an array of Thing IDs.
            try:
                specifics = specifics.split()
            except AttributeError:
                if specifics != 0: 
                    raise AttributeError("specifics is not splittable.")
            
            try:
                # Changes specifics into an array of Things.
                for i, x in enumerate(specifics):
                    if x:
                        print("Working! ", i, x)
                        specifics[i] = self.things[self.thing_names[x]]
                        
                # Calls the action, returning an array of instructions.
                bp_code = action.call(specifics)
                    
                # Runs these instructions.
                for x in bp_code: self.blueprint_main(x)
            
            # If one of the item IDs doesn't correspond to the ID of a 
            # Thing, put a "Cannot be found." message.
            except KeyError:
                self._puts(self.ERROR["act_item_not_found"])
                           
        return
        
    def _special_act(self, action, specifics):
        if action == "take":
            try: specifics = self._alias(specifics)
            except NameError: pass
            
            if specifics == "room":
                if V: print("Taking: Room.")
                self._puts(self.ERROR["act_using_rooms"])
            elif specifics in self.loc.holding:
                if V: print("Taking: ", specifics)
                if specifics.isProp:
                    self._puts(self.ERROR["act_taking_prop"])
                else:
                    self.inventory.add_item(specifics)
                    self.loc.holding.remove(specifics)
                    self._puts("Picked up the " + specifics.name + ".")
            ## elif specifics in self.inventory.holding:
            ##     self._puts(self.ERROR["act_already_holding"])
            else:
                self._puts(self.ERROR["act_item_not_found"])
                    
    def _user_act(self, action, specifics):
        raise NotImplementedError
    
    def _inv(self, command):
        """ Inventory menu commands. """
        if command == "open":
            self._puts(self.inventory.__str__())
        else: pass
        return

    
# ----------------------- Blueprint Implementation --------------------------
    
    def blueprint_main(self, words):
        """ Main function for Blueprint code.
        
        Takes a string of BP code and splits it up into a 
        pre-functional character, functional character, and a
        post-functional character. """
        if words == "pass": return
        print("INPUT: "+ str(words))
        type_code = words[:3]
        
        finder = re.search(Game.blueprint_keywords, words)
        if finder is None:
            self._puts("MCode lacking functional character: " + words)
            raise AttributeError("No functional character found.")
        
        functional_char = words[finder.span()[0]]
        target = words[4:finder.span()[0]]
        parameters = words[finder.span()[1]:]
        #if type_code == 'prp': type_code = 'obj'
        getattr(self, type_code+"_func")(functional_char, target, parameters)
        #self._puts(type_code, functional_char, parameters)
        return
    
    def _alias(self, target):
        """ Turns a name into its appropriate room or thing. """
        
        if target == '_':
            return self.loc
        elif target == '$':
            return self.inventory
        elif target in self.rooms:
            return self.rooms[target]
        elif target in self.thing_names:
            return self.things[self.thing_names[target]]
        else:
            raise NameError(target + " not a Thing, Room, or alias.")
        
    def ift_func(self, functional_char, thing_in_question,
                 condition):
        """ Conditional blueprint processor.
        
        Isolates the condition from the post-functional part and enters an 
        if-ifelse-else structure to find which condition corresponds to
        the Blueprint code. 
        
        If condition is true, runs each BP code line found after the >
        (separated by }) by calling blueprint_main. Otherwise, runs BP code
        found after the <. """
                 
        # < divides the "on true" command from the "on false" one.
        condition = condition.split('<')
        else_condition = condition[1].split('}')
        condition = condition[0].split('}')
        
        # At this point condition has the following form:
        #          [parameter>mcode0, mcode1, mcode2,...]
        # We split up the parameter and the mcode0 part using the >,
        # assign parameter to second_thing, and assign mcode0 to condition[0].
        then_finder = re.search('>', condition[0])
        try:
            second_thing = condition[0][:then_finder.span()[0]]
            condition[0] = condition[0][then_finder.span()[1]:]
        except AttributeError:
            raise AttributeError("> not found.")
        
        # Turns second_thing into a class instance.
        second_thing = self._alias(second_thing)        
        

        ### Redo inventory isHolding checks.
        # @: True if thing_in_question is in second_thing, where second_thing
        #    must be a room or an inventory (with a "holding" attribute).
        if functional_char == '@':
            try:
                if thing_in_question in second_thing.holding:
                    status = True
                else: 
                    status = False
            except KeyError:
                raise AttributeError("@ error.\n"+ second_thing.name + 
                                     " has no holding attribute.")

        # = : True if thing_in_question is identical with second_thing.
        #     Generally used in conjunction with the _ alias.
        elif functional_char == '=':
            if thing_in_question == second_thing:
                status = True
            else:
                status = False
                
        tmp = condition if status else else_condition
        for i in tmp: self.blueprint_main(i)
        
        return
    
    def sys_func(self, functional_char, target, instruct):
        """ System mcode processor. Used to print messages to the terminal. """
        if V: self._puts("### Entering system functions.")
        if functional_char == '!':
            self._puts(instruct)
        else:
            pass
        return
    
    ### Inventory complication project continues onwards.
    def inv_func(self, functional_char, target, instruct):
        """ Inventory mcode processor. Used for storage operations. """
        if V: self._puts("### Entering inventory functions.")
        
        if functional_char == '+':
            self.inventory.add_item(target)
        elif functional_char == '-':
            self.inventory.remove_item(target)
        else:
            pass
        return
    

    ### Do some cleaning up here.
    def rom_func(self, functional_char, target, instruct):
        """ Room mcode processor. Used to manipulate Rooms. """
        if V: self._puts("### Entering room functions.")

        #tmp_instruct = ' '.join(instruct)
        tmp_instruct = instruct
        
        # Changes a room name or _ into a Room class instance.
        target = self._alias(target)
        
        ### Aren't they suppose.d to hold instances, not names?
        if functional_char == '+':
            target.holding.append(tmp_instruct)
        elif functional_char == '-':
            target.holding.remove(tmp_instruct)
            
        elif functional_char == '&':
            self._link(target, instruct[0], instruct[1:])
            
        ### Make sure this works properly.
        elif functional_char == '#':
            try:
                attr = Room.codes['#' + instruct[:2]]
            except KeyError:
                raise AttributeError("No corresponding Room attribute.")
            self.change_var(target, attr, instruct[2:])
        return

    def obj_func(self, functional_char, target, instruct):
        """ Thing mcode processor. Used to manipulate Things. """
        if V: self._puts("### Entering object functions.")
        
        target = self._alias(target)
        
        ### Give this a looksee.
        if functional_char == '#':
            try:
                attr = Thing.codes['#'+instruct[:2]]
            except KeyError:
                raise AttributeError("No corresponding Thing attribute.")
            #self.change_var(target, attr, instruct[2:])
            if V: self._puts("#### Setting the new attribute now.")
            setattr(getattr(self, "things")[target.alias], attr, instruct[2:])
        return
    
    ### Is this even used?
    def change_var(self, target, attribute, new_desc):
        """ Tertiary function used to change the attributes of instances of
            Room and Thing. """
        try:
            setattr(target, attribute, new_desc) 
        except AttributeError:
            raise AttributeError(target + " does not have attribute "
                                        + attribute)
        return        
    
    ## Should probably be a Room staticmethod.
    def _link(self, source, direction, dest, isEuclidean = True):
        """ Tertiary function; establishes links between rooms.
                source ----direction----> dest
            If isEuclidean:
                dest ----opposite_dir----> source
            where opposite_dir should be clear. (N <-> S, W <-> E) """
            
        direction = self.cardinals[direction.lower()]
        dest = self._alias(dest)
        
        if isEuclidean:
            if source == dest:
                raise Error("Euclidean rooms enabled; no loops allowed.")
        source.links[direction] = dest.name
        if isEuclidean:
            if direction == 0: direction = 3
            elif direction == 1: direction = 2
            elif direction == 2: direction = 1
            elif direction == 3: direction = 0
            dest.links[direction] = source.name
        return

    '''
    def _on_entry(self):
        self._puts(self.loc.on_entry(), True)
        self._puts(
                Thing.thing_printer( \
                    [self.things[x] for x in self.loc.holding]),True)
        return
    '''

# --------------------------- GUI/Game Interface ----------------------------
    
    def _room_update(self):
        thing_info = Thing.thing_printer(self.loc.holding)
        setting_info = self.loc.on_entry() + '\n'
        if thing_info:
            setting_info += thing_info + '\n'
        self._puts(setting_info, True)
        return

    ''' Main function. Takes user input, passes it to prompt_exe. '''
    def main(self):
        self._puts(self.GAME_MSGS['beginning'])
        self._room_update()
        #raise NameError("Game finished.")
        return
        
    def cliMain(self):
        self.main()
        prompt = ' '
        while (prompt[0] != 'q' and prompt[0] != 'quit'):
            print(self.gets())
            prompt = input('> ').lower()
            ##prompt = x.split() if x != '' else ''
            if prompt == '': prompt = ' '
            self.prompt_exe(prompt)        

    """ Functions which are involved in passing to GUI_Holder class. """
    def _puts(self, input_string, isSetting = False):
        if isSetting:
            self.setting_output = input_string
        else:
            self.action_output += input_string + '\n'

    def gets(self):
        self._room_update()
        returning = self.setting_output + '\n' + self.action_output
        self.action_output = ''
        return returning

# ------------------------- Testing -----------------------------------------

def test_init():
    with File_Processor('testgame_desc.txt') as F:
        G = Game(F.room_info, F.thing_info, F.action_info, None)
    return G

if __name__ == "__main__":
    G = test_init()
    G.cliMain()
