import cmd
import sys
import os
import os.path as op
import posixpath as pp
import compass_model

from . import container
from . import array
from . import image
from . import keyvalue


# open stores
_instances = []

class StoreView:
    def __init__(self, store):
        self._store = store
        self._container = container.ContainerFrame(store.root)


def open_node(node, pos=None):
    """ Open a viewer frame appropriate for the given Node instance.
    
    node:   Node instance to open
    pos:    2-tuple with current window position (used to avoid overlap).
    """
    
    if pos is not None:
        # The thing we get from GetPosition isn't really a tuple, so
        # you have to manually cast entries to int or it silently fails.
        newpos =(int(pos[0])+80, int(pos[1])+80)
    else:
        newpos = None

    if isinstance(node, compass_model.Container):
        f = container.ContainerFrame(node)
        f.Show()
    elif isinstance(node, compass_model.Array):
        f = array.ArrayFrame(node)
        f.Show()
        print "no array frame"
    elif isinstance(node, compass_model.KeyValue):
        f = keyvalue.KeyValueFrame(node)
        f.Show()
        print "no key value frame"
    elif isinstance(node, compass_model.Image):
        f = image.ImageFrame(node)
        f.Show()
        print "no image frame"
    else:
        pass

def open_store(url):
    """ Open the url using the first matching registered Store class.

    Returns True if the url was successfully opened, False otherwise.
    """
    
    # see if the store is already opened
    for storeview in _instances:
        if storeview._store.url == url:
            return storeview._store;  # already opened
            
    stores = [x for x in compass_model.getstores() if x.canhandle(url)]

    if len(stores) > 0:
        instance = stores[0](url)
        # open_node(instance.root)
        storeView = StoreView(instance)
        _instances.append(storeView)
        
        return instance

    return None
        

class CompassShell(cmd.Cmd):
    currentInstance = None  
    
    def do_pwd(self, line):
        "Print current system directory"
        print op.realpath('.')
    
    def do_shell(self, s):
        "execute shell commands (can also use '!' to invoke)"
        os.system(s)
    
    def do_eval(self, line):
        "evaluate given python expression"
        print 'line:', line
        try:
            s = eval(line)
            print s
        except SyntaxError, e:
            print 'invalid syntax', e
        
        
    def do_show_stores(self, line):
        "show available stores"
        for store in compass_model.getstores():
            print store.__name__
            
            
    def do_show_filters(self, line):
        "show availble file filters"
        for store in compass_model.getstores():
            if store.file_extensions:
                for file_type in store.file_extensions.keys():
                    print file_type, store.file_extensions[file_type]

                     
    def do_cwd(self, line):
        "change working directory"
        try:
            os.chdir(line)
            print op.realpath('.')
        except OSError, e:
            print 'invalid path', line
        
        
    def do_open(self, line):
        "open a file (or provide a number to activate one of the currently opened stores)"
        if not line:
            # show opened stores
            if len(_instances) == 0:
                print "no opened files"
                return
            cnt = 1
            for storeView in _instances:
                marker = ' '
                if storeView == self.currentInstance:
                    marker = '>'
                print marker, cnt, storeView._store.displayname
                cnt = cnt + 1
            return
        storeView = None
        if line.isdigit() and len(_instances) <= line:
        # open nth instance
            index = int(line) - 1
            storeView = _instances[index]
        if not storeView:   
        # create a file path   
            filename = op.realpath(line)
            url = 'file://'+filename
            print "opening:", url
            instance = open_store(url)
            if instance:
                print len(_instances) 
                print instance.__class__
                storeView = StoreView(instance)
        
        if storeView:
            node = storeView._store.root
            print node.displaytitle
            print node.description
            self.currentInstance = storeView
            
        else:
            print 'there was a problem opening the file'
                 
    def do_close(self, line):
        "close store (enter number of store listed in 'show_stores'"
        storeView = None
        resetCurrent = False
        if line.isdigit() and len(_instances) <= line:
        # close nth instance
            index = int(line) - 1
            storeView = _instances[index]
            if storeView == self.currentInstance:
                resetCurrent = True
            storeView._store.close()
            _instances.remove(storeView)
        else:
            print "provide number of store to close"
            
        if resetCurrent:
            if len(_instances) == 0:
                self.currentInstance = None
            else:
                self.currentInstance = _instances[0]
                
    def do_show(self, line):
        "Show information about the current object"
        if self.currentInstance == None:
            print "nothing to show"
            return
        self.currentInstance._container.Show(line)
        
    def do_go(self, line):
        "Go to the given group or path"
        if self.currentInstance == None:
            print "open a file first!"
            return
        if len(line) == 0:
            print "Usage: go [object_name | path]"
            return
        store = self.currentInstance._store
        node = self.currentInstance._container.node
        path = pp.join(node.key, line)
        # print 'new path', path
        if node.canhandle(store, path):
            newNode = store[path]
            self.currentInstance._container.go(newNode)
            print newNode.displayname
        else:
            print "this is not a valid path:", path
            
    def do_back(self, line):
        "Go back to previous object"
        if self.currentInstance == None:
            print "nothing to go back from"
            return
        container = self.currentInstance._container
        container.go_back()
        print container.node.displayname
        
    def do_next(self, line):
        "Go forward to next object"
        if self.currentInstance == None:
            print "nothing to go forward to"
            return
        container = self.currentInstance._container
        container.go_next()
        print container.node.displayname
        
    def do_up(self, line):
        "Go to parent object"
        if self.currentInstance == None:
            print "no object is open"
            return
        container = self.currentInstance._container
        container.go_up()
        print container.node.displayname
        
    
        
        
        
        
            
    def do_quit(self, line):
        "Quit the shell"
        for instance in _instances:
            instance._store.close()
            
        return True;
        
    
    FRIENDS = [ 'Alice', 'Adam', 'Barbara', 'Bob' ]
    
    def do_greet(self, person):
        "Greet the person"
        if person and person in self.FRIENDS:
            greeting = 'hi, %s!' % person
        elif person:
            greeting = "hello, " + person
        else:
            greeting = 'hello'
        print greeting
    
    def complete_greet(self, text, line, begidx, endidx):
        if not text:
            completions = self.FRIENDS[:]
        else:
            completions = [ f
                            for f in self.FRIENDS
                            if f.startswith(text)
                            ]
        return completions


def run():
    # These are imported to register their classes with
    # compass_model.  We don't use them directly.
    import filesystem_model
    import array_model
    import hdf5_model
    import asc_model
    CompassShell().cmdloop()

if __name__ == '__main__':
    CompassShell().cmdloop()

