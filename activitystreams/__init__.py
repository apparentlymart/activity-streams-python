

class Activity(object):
    actor = None
    object = None
    target = None
    verb = None
    time = None
    generator = None
    icon_url = None
    service_provider = None
    links = None

    def __init__(self, actor=None, object=None, target=None, verb=None, time=None, generator=None, icon_url=None, service_provider=None, links=None):
        self.actor = actor
        self.object = object
        self.target = target
        self.verb = verb
        self.time = time
        self.service_provider = service_provider
        self.generator = generator
        self.icon_url = icon_url

        if links is not None:
            self.links = links
        else:
            self.links = []

class Object(object):
    id = None
    name = None
    url = None
    object_type = None
    summary = None
    image = None
    in_reply_to_object = None
    attached_objects = None
    reply_objects = None
    reaction_activities = None
    action_links = None
    upstream_duplicate_ids = None
    downstream_duplicate_ids = None

    def __init__(self, id=None, name=None, url=None, object_type=None, summary=None, image=None, in_reply_to_object=None, attached_objects=None, reply_objects=None, reaction_activities=None, action_links=None, upstream_duplicate_ids=None, downstream_duplicate_ids=None):
        self.id = id
        self.name = name
        self.url = url
        self.object_type = object_type
        self.summary = summary
        self.image = image
        self.in_reply_to_object = in_reply_to_object

        if attached_objects is not None:
            self.attached_objects = attached_objects
        else:
            self.attached_objects = []

        if reply_objects is not None:
            self.reply_objects = reply_objects
        else:
            self.reply_objects = []

        if reaction_activities is not None:
            self.reaction_activities = reaction_activities
        else:
            self.reaction_activities = []

        if action_links is not None:
            self.action_links = action_links
        else:
            self.action_links = []

        if upstream_duplicate_ids is not None:
            self.upstream_duplicate_ids = upstream_duplicate_ids
        else:
            self.upstream_duplicate_ids = []

        if downstream_duplicate_ids is not None:
            self.downstream_duplicate_ids = downstream_duplicate_ids
        else:
            self.downstream_duplicate_ids = []


class MediaLink(object):
    url = None
    media_type = None
    width = None
    height = None
    duration = None

    def __init__(self, url=None, media_type=None, width=None, height=None, duration=None):
        self.url = url
        self.media_type = media_type
        self.width = width
        self.height = height
        self.duration = duration


class ActionLink(object):
    url = None
    caption = None

    def __init__(self, url=None, caption=None):
        self.url = url
        self.caption = caption


class Link(object):
    url = None
    media_type = None
    rel = None

    def __init__(self, url=None, media_type=None, rel=None):
        self.url = url
        self.media_type = media_type
        self.rel = rel





