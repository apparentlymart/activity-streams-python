

class Activity(object):
    actor = None
    object = None
    target = None
    verbs = None
    time = None
    generator = None

    def __init__(self, actor=None, object=None, target=None, verbs=None, time=None, generator=None):
        self.actor = actor
        self.object = object
        self.target = target
        if verbs is not None:
            self.verbs = verbs
        else:
            self.verbs = []
        self.time = time
        self.generator = generator

class Object(object):
    id = None
    name = None
    url = None
    object_types = None

    def __init__(self, id=None, name=None, url=None, object_types=None):
        self.id = id
        self.name = name
        self.url = url
        if object_types is not None:
            self.object_types = object_types
        else:
            self.object_types = []

