

class Activity(object):
    actor = None
    object = None
    target = None
    verbs = None
    time = None
    generator = None
    icon_url = None

    def __init__(self, actor=None, object=None, target=None, verbs=None, time=None, generator=None, icon_url=None):
        self.actor = actor
        self.object = object
        self.target = target
        if verbs is not None:
            self.verbs = verbs
        else:
            self.verbs = []
        self.time = time
        self.generator = generator
        self.icon_url = icon_url


class Object(object):
    id = None
    name = None
    url = None
    image_url = None
    summary = None
    object_types = None

    def __init__(self, id=None, name=None, url=None, object_types=None, summary=None, image_url=None):
        self.id = id
        self.name = name
        self.url = url
        self.image_url = image_url
        self.summary = summary
        if object_types is not None:
            self.object_types = object_types
        else:
            self.object_types = []

