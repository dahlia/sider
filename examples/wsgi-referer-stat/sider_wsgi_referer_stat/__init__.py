r""":mod:`sider.ext.wsgi_referer_stat` --- Collecting referers using sorted sets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example will show you when and how to use sorted sets basically.
We will build a small :pep:`WSGI <333>` middleware that simply collects
all :mailheader:`Referer` of the given WSGI web application.

"""
from sider.session import Session
from sider.types import SortedSet
from jinja2 import Environment, PackageLoader


class RefererStatMiddleware(object):
    """A simple WSGI middleware that collects :mailheader:`Referer`
    headers and stores it into a Redis sorted set.

    You can see the list of referrers ordered by duplication count
    in ``/__stat__`` page (or you can configure the ``stat_path``
    argument).

    :param session: sider session object
    :type session: :class:`sider.session.Session`
    :param set_key: the key name of Redis sorted set
                    to store data
    :type set_key: :class:`basestring`
    :param application: wsgi app to wrap
    :type application: :class:`collections.Callable`
    :param stat_path: path to see the collected data.
                      default is ``'/__stat__'``.
                      if it's ``None`` the data cannot be accessed
                      from outside
    :type stat_path: :class:`basestring`

    """

    def __init__(self, session, set_key, application, stat_path='/__stat__'):
        if not isinstance(session, Session):
            raise TypeError('session must be an instance of sider.session.'
                            'Session, not ' + repr(session))
        elif not callable(application):
            raise TypeError('application must be callable, not ' +
                            repr(application))
        self.session = session
        self.application = application
        self.referer_set = session.get(str(set_key), SortedSet)
        self.stat_path = stat_path
        loader = PackageLoader(__name__)
        environment = Environment(loader=loader)
        self.template = environment.get_template('stat.html')

    def stat_application(self, environ, start_response):
        content_type = 'text/html; charset=utf-8'
        start_response('200 OK', [('Content-Type', content_type)])
        referers = self.referer_set.items(reverse=True)
        stream = self.template.generate(referers=referers)
        for chunk in stream:
            yield chunk.encode('utf-8', 'ignore')

    def __call__(self, environ, start_response):
        if self.stat_path is not None:
            path = environ['PATH_INFO']
            if path == self.stat_path or path.startswith(self.stat_path + '/'):
                return self.stat_application(environ, start_response)
        try:
            referer = environ['HTTP_REFERER']
        except KeyError:
            pass
        else:
            self.referer_set.add(referer)
        return self.application(environ, start_response)

