

from activitystreams import Activity, Object, MediaLink, ActionLink, Link


import re
import datetime
import time


def make_activities_from_stream_dict(stream_dict):
    activities = []

    for activity_dict in stream_dict["items"]:
        activities.append(make_activity_from_activity_dict(activity_dict))

    return activities


def make_activity_from_activity_dict(activity_dict, implied_object=None):
    object_dict = None
    actor_dict = None
    target_dict = None
    generator_dict = None
    service_provider_dict = None
    verb = None
    published_datetime = None

    object = None
    if implied_object is not None:
        object = implied_object
    else:
        if "object" in activity_dict:
            object_dict = activity_dict["object"]
            object = make_object_from_object_dict(object_dict)

    if "actor" in activity_dict:
        actor_dict = activity_dict["actor"]

    if "target" in activity_dict:
        target_dict = activity_dict["target"]

    if "generator" in activity_dict:
        generator_dict = activity_dict["generator"]

    if "provider" in activity_dict:
        service_provider_dict = activity_dict["provider"]

    if "postedTime" in activity_dict:
        published_w3cdtf = activity_dict["postedTime"]
        published_datetime = _parse_date_w3cdtf(published_w3cdtf)

    if "verb" in activity_dict:
        verb = activity_dict["verb"]

    return Activity(
        object=object,
        actor=make_object_from_object_dict(actor_dict),
        target=make_object_from_object_dict(target_dict),
        generator=make_object_from_object_dict(generator_dict),
        service_provider=make_object_from_object_dict(service_provider_dict),
        time=published_datetime,
        verb=verb
        )


def make_object_from_object_dict(object_dict, implied_in_reply_to_object=None):

    if object_dict is None:
        return None

    id = None
    name = None
    summary = None
    image = None
    url = None
    object_type = None
    in_reply_to_object = None
    reply_objects = []
    reaction_activities = []
    attached_objects = []
    upstream_duplicate_ids = []
    downstream_duplicate_ids = []
    links = []

    if "id" in object_dict:
        id = object_dict["id"]

    if "displayName" in object_dict:
        name = object_dict["displayName"]

    if "summary" in object_dict:
        summary = object_dict["summary"]

    if "permalinkUrl" in object_dict:
        url = object_dict["permalinkUrl"]

    if "objectType" in object_dict:
        object_type = object_dict["objectType"]

    if "image" in object_dict:
        image = make_media_link_from_media_link_dict(object_dict["image"])

    # FIXME: implement the rest of the components

    return Object(
        id=id,
        name=name,
        summary=summary,
        image=image,
        url=url,
        object_type=object_type,
        in_reply_to_object=in_reply_to_object,
        reply_objects=reply_objects,
        reaction_activities=reaction_activities,
        attached_objects=attached_objects,
        upstream_duplicate_ids=upstream_duplicate_ids,
        downstream_duplicate_ids=downstream_duplicate_ids,
        links=links,
        )


def make_media_link_from_media_link_dict(media_link_dict):
    url = None
    width = None
    height = None
    duration = None

    if "url" in media_link_dict:
        url = media_link_dict["url"]

    if "width" in media_link_dict:
        width = media_link_dict["width"]

    if "height" in media_link_dict:
        height = media_link_dict["height"]

    if "duration" in media_link_dict:
        duration = media_link_dict["duration"]

    return MediaLink(
        url=url,
        width=width,
        height=height,
        duration=duration,
        )



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
