from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom

argspec = {'ls': {'min':1,'max':2}, 'mkdir': {'min':2,'max':2},
       'cd': {'min':1,'max':2}, 'pwd': {'min':1,'max':1},
       'cp': {'min':2,'max':3}, 'mv': {'min':2,'max':3},
       'rm': {'min':2,'max':2}, 'rmdir': {'min':2,'max':2},
       'cat': {'min':2,'max':5}, 'less': {'min':2,'max':2},
       'head': {'min':2,'max':2}, 'tail': {'min':2,'max':2},
       'grep': {'min':3,'max':3}, 'wc': {'min':2,'max':2},
       'sort': {'min':1,'max':1}, 'who': {'min':1,'max':1},
       'history': {'min':1,'max':1}, '!':{'min':2,'max':2},
       'chmod': {'min':2,'max':2}}

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def xmlFactory(arglist):
    root = Element('head')
    for cmd in arglist:
        command = SubElement(root, "command", {'arg':cmd})
        print(cmd)
        minimun = SubElement(command, "length", {"minimum":str(arglist[cmd]['min']), "maximum":str(arglist[cmd]['max'])})

    xml = prettify(root)
    print(xml)

xmlFactory(argspec)
