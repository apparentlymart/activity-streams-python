

from activitystreams import Activity, Object, MediaLink, ActionLink, Link


import re
import datetime
import time


class AtomActivity(Activity):
    pass


# This is a weird enum-like thing.
class ObjectParseMode(object):
    def __init__(self, reprstring):
        self.reprstring = reprstring

    def __repr__(self):
        return self.reprstring
ObjectParseMode.ATOM_ENTRY = ObjectParseMode("ObjectParseMode.ATOM_ENTRY")
ObjectParseMode.ATOM_AUTHOR = ObjectParseMode("ObjectParseMode.ATOM_AUTHOR")
ObjectParseMode.ACTIVITY_OBJECT = ObjectParseMode("ObjectParseMode.ACTIVITY_OBJECT")


ATOM_PREFIX = "{http://www.w3.org/2005/Atom}"
ACTIVITY_PREFIX = "{http://activitystrea.ms/spec/1.0/}"
MEDIA_PREFIX = "{http://purl.org/syndication/atommedia}"

ATOM_FEED = ATOM_PREFIX + "feed"
ATOM_ENTRY = ATOM_PREFIX + "entry"
ATOM_ID = ATOM_PREFIX + "id"
ATOM_AUTHOR = ATOM_PREFIX + "author"
ATOM_SOURCE = ATOM_PREFIX + "source"
ATOM_TITLE = ATOM_PREFIX + "title"
ATOM_SUMMARY = ATOM_PREFIX + "summary"
ATOM_CONTENT = ATOM_PREFIX + "content"
ATOM_LINK = ATOM_PREFIX + "link"
ATOM_PUBLISHED = ATOM_PREFIX + "published"
ATOM_NAME = ATOM_PREFIX + "name"
ATOM_URI = ATOM_PREFIX + "uri"
ATOM_GENERATOR = ATOM_PREFIX + "generator"
ATOM_ICON = ATOM_PREFIX + "icon"
ACTIVITY_SUBJECT = ACTIVITY_PREFIX + "subject"
ACTIVITY_OBJECT = ACTIVITY_PREFIX + "object"
ACTIVITY_OBJECT_TYPE = ACTIVITY_PREFIX + "object-type"
ACTIVITY_VERB = ACTIVITY_PREFIX + "verb"
ACTIVITY_TARGET = ACTIVITY_PREFIX + "target"
ACTIVITY_ACTOR = ACTIVITY_PREFIX + "actor"
POST_VERB = "http://activitystrea.ms/schema/1.0/post"
MEDIA_WIDTH = MEDIA_PREFIX + "width"
MEDIA_HEIGHT = MEDIA_PREFIX + "height"
MEDIA_DURATION = MEDIA_PREFIX + "duration"
MEDIA_DESCRIPTION = MEDIA_PREFIX + "description"


def make_activities_from_feed(et):
    feed_elem = et.getroot()
    entry_elems = feed_elem.findall(ATOM_ENTRY)

    activities = []

    for entry_elem in entry_elems:
        activities.extend(make_activities_from_entry(entry_elem, feed_elem))

    return activities


def make_activities_from_entry(entry_elem, feed_elem):
    object_elems = entry_elem.findall(ACTIVITY_OBJECT)

    activity_is_implied = False

    if len(object_elems) == 0:
        # Implied activity, so the entry itself represents the object.
        activity_is_implied = True
        object_elems = [ entry_elem ]

    author_elem = entry_elem.find(ATOM_AUTHOR)
    if author_elem is None:
        source_elem = entry_elem.find(ATOM_SOURCE)
        if source_elem is not None:
            author_elem = source_elem.find(ATOM_AUTHOR)
        if author_elem is None:
            author_elem = feed_elem.find(ATOM_AUTHOR)

    target_elem = entry_elem.find(ACTIVITY_TARGET)

    published_elem = entry_elem.find(ATOM_PUBLISHED)
    published_datetime = None
    if published_elem is not None:
        published_w3cdtf = published_elem.text
        published_datetime = _parse_date_w3cdtf(published_w3cdtf)

    verb_elem = entry_elem.find(ACTIVITY_VERB)
    verb = None
    if verb_elem is not None:
        verb = verb_elem.text
    else:
        verb = POST_VERB

    generator_elem = entry_elem.find(ATOM_GENERATOR)

    icon_url = None
    icon_elem = entry_elem.find(ATOM_ICON)
    if icon_elem is not None:
        icon_url = icon_elem.text

    target = None
    if target_elem:
        target = make_object_from_elem(target_elem, feed_elem, ObjectParseMode.ACTIVITY_OBJECT)

    actor = None
    if author_elem:
        actor = make_object_from_elem(author_elem, feed_elem, ObjectParseMode.ATOM_AUTHOR)

    activities = []
    for object_elem in object_elems:
        if activity_is_implied:
            object = make_object_from_elem(object_elem, feed_elem, ObjectParseMode.ATOM_ENTRY)
        else:
            object = make_object_from_elem(object_elem, feed_elem, ObjectParseMode.ACTIVITY_OBJECT)

        activity = Activity(object=object, actor=actor, target=target, verb=verb, time=published_datetime, icon_url=icon_url)
        activities.append(activity)

    return activities


def make_object_from_elem(object_elem, feed_elem, mode):

    id = None
    id_elem = object_elem.find(ATOM_ID)
    if id_elem is not None:
        id = id_elem.text

    summary = None
    summary_elem = object_elem.find(ATOM_SUMMARY)
    if summary_elem is not None:
        summary = summary_elem.text

    name_tag_name = ATOM_TITLE
    # The ATOM_AUTHOR parsing mode looks in atom:name instead of atom:title
    if mode == ObjectParseMode.ATOM_AUTHOR:
        name_tag_name = ATOM_NAME
    name = None
    name_elem = object_elem.find(name_tag_name)
    if name_elem is not None:
        name = name_elem.text

    url = None
    image = None
    for link_elem in object_elem.findall(ATOM_LINK):
        type = link_elem.get("type")
        rel = link_elem.get("rel")
        if rel is None or rel == "alternate":
            if type is None or type == "text/html":
                url = link_elem.get("href")
        if rel == "preview":
            if type is None or type == "image/jpeg" or type == "image/gif" or type == "image/png":
                # FIXME: Should pull out the width/height/duration attributes from AtomMedia too.
                image = MediaLink(url=link_elem.get("href"))

    # In the atom:author parse mode we fall back on atom:uri if there's no link rel="alternate"
    if url is None and mode == ObjectParseMode.ATOM_AUTHOR:
        uri_elem = object_elem.find(ATOM_URI)
        if uri_elem is not None:
            url = uri_elem.text

    object_type_elem = object_elem.find(ACTIVITY_OBJECT_TYPE)
    object_type = None
    if object_type_elem is not None:
        object_type = object_type_elem.text

    return Object(id=id, name=name, url=url, object_type=object_type, image=image, summary=summary)


# This is pilfered from Universal Feed Parser.
def _parse_date_w3cdtf(dateString):
    def __extract_date(m):
        year = int(m.group('year'))
        if year < 100:
            year = 100 * int(time.gmtime()[0] / 100) + int(year)
        if year < 1000:
            return 0, 0, 0
        julian = m.group('julian')
        if julian:
            julian = int(julian)
            month = julian / 30 + 1
            day = julian % 30 + 1
            jday = None
            while jday != julian:
                t = time.mktime((year, month, day, 0, 0, 0, 0, 0, 0))
                jday = time.gmtime(t)[-2]
                diff = abs(jday - julian)
                if jday > julian:
                    if diff < day:
                        day = day - diff
                    else:
                        month = month - 1
                        day = 31
                elif jday < julian:
                    if day + diff < 28:
                       day = day + diff
                    else:
                        month = month + 1
            return year, month, day
        month = m.group('month')
        day = 1
        if month is None:
            month = 1
        else:
            month = int(month)
            day = m.group('day')
            if day:
                day = int(day)
            else:
                day = 1
        return year, month, day

    def __extract_time(m):
        if not m:
            return 0, 0, 0
        hours = m.group('hours')
        if not hours:
            return 0, 0, 0
        hours = int(hours)
        minutes = int(m.group('minutes'))
        seconds = m.group('seconds')
        if seconds:
            seconds = int(float(seconds))
        else:
            seconds = 0
        return hours, minutes, seconds

    def __extract_tzd(m):
        '''Return the Time Zone Designator as an offset in seconds from UTC.'''
        if not m:
            return 0
        tzd = m.group('tzd')
        if not tzd:
            return 0
        if tzd == 'Z':
            return 0
        hours = int(m.group('tzdhours'))
        minutes = m.group('tzdminutes')
        if minutes:
            minutes = int(minutes)
        else:
            minutes = 0
        offset = (hours*60 + minutes) * 60
        if tzd[0] == '+':
            return -offset
        return offset

    __date_re = ('(?P<year>\d\d\d\d)'
                 '(?:(?P<dsep>-|)'
                 '(?:(?P<julian>\d\d\d)'
                 '|(?P<month>\d\d)(?:(?P=dsep)(?P<day>\d\d))?))?')
    __tzd_re = '(?P<tzd>[-+](?P<tzdhours>\d\d)(?::?(?P<tzdminutes>\d\d))|Z)'
    __tzd_rx = re.compile(__tzd_re)
    __time_re = ('(?P<hours>\d\d)(?P<tsep>:|)(?P<minutes>\d\d)'
                 '(?:(?P=tsep)(?P<seconds>\d\d(?:[.,]\d+)?))?'
                 + __tzd_re)
    __datetime_re = '%s(?:T%s)?' % (__date_re, __time_re)
    __datetime_rx = re.compile(__datetime_re)
    m = __datetime_rx.match(dateString)
    if (m is None) or (m.group() != dateString): return
    gmt = __extract_date(m) + __extract_time(m) + (0, 0, 0)
    if gmt[0] == 0: return
    return datetime.datetime.utcfromtimestamp(time.mktime(gmt) + __extract_tzd(m) - time.timezone)
