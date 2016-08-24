import livestreamer
NAME = 'Livestreamer'
PREFIX = '/video/livestreamer'
ICON = 'icon-default.png'
DEFAULT_PLAYLIST = 'default.json'

def Start():
    ObjectContainer.title1 = NAME
    load_file(DEFAULT_PLAYLIST)


@handler(PREFIX, NAME, ICON)
def MainMenu():
    oc = ObjectContainer(no_cache=True)
    for item in Dict['playlist']:
        oc.add(DirectoryObject(
            key=Callback(Qualities, title=unicode(item['name']), url=item['url']),
            title=unicode(item['name'])))
    oc.add(DirectoryObject(
        key=Callback(load_file, file_name=DEFAULT_PLAYLIST),
        title=u'Reload {}'.format(DEFAULT_PLAYLIST)))
    return oc


def stream_type(stream):
    """ get a string for the stream type """
    if isinstance(stream, livestreamer.stream.HLSStream):
        return "HLSStream"
    elif isinstance(stream, livestreamer.stream.HDSStream):
        return "HDSStream"
    elif isinstance(stream, livestreamer.stream.AkamaiHDStream):
        return "AkamaiHDStream"
    elif isinstance(stream, livestreamer.stream.HTTPStream):
        return "HTTPStream"
    elif isinstance(stream, livestreamer.stream.RTMPStream):
        return "RTMPStream"
    return None


@route(PREFIX+'/loadfile')
def load_file(file_name):
    try:
        data = JSON.ObjectFromString(Resource.Load(file_name))
    except Exception:
        Log("Unable to load file.")
        return ObjectContainer()
    else:
        Dict['playlist'] = data
    return ObjectContainer()


@route(PREFIX+'/qualities')
def Qualities(title, url):
    """ get streams from url with livestreamer, list the qualities """
    oc = ObjectContainer()
    try:
        streams = livestreamer.streams(url)
    except livestreamer.NoPluginError:
        Log("Livestreamer can't handle the url %s" % url)
        return oc
    except livestreamer.PluginError as err:
        Log("Livestreamer plugin error: %s" % err)
        return oc

    new_streams = list()
    for quality in streams:
        st = stream_type(streams[quality])
        if (st == "HLSStream") or (st == "HTTPStream"):
            new_streams.append(u"{}|{}|{}".format(st, quality, streams[quality].url))

    if not new_streams:
        return ObjectContainer(header="Warning", message=u"No Streams for '{}'".format(url))

    final_streams = "livestreamer://" + '||'.join(new_streams)
    oc.add(VideoClipObject(url=final_streams, title=title))

    return oc
