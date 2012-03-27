#!/usr/bin/env python
"""Sider release script
~~~~~~~~~~~~~~~~~~~~~~~

"""
import re
import os.path
import mimetypes
try:
    from collections import OrderedDict as odict
except ImportError:
    from odict import odict  # IF YOU SEE ImportError, DO `easy_install odict`
import requests  # IF YOU SEE ImportError, DO `easy_install requests`


class BitbucketClient(object):
    """Minimal Bitbucket that signs in and uploads files."""

    def __init__(self, username, password, repository):
        self.session = requests.session()
        self.signin(username, password)
        self.repository = repository

    def signin(self, username, password):
        url = 'https://bitbucket.org/account/signin/'
        form = self.session.get(url)
        token = self._find_field(form.content, 'csrfmiddlewaretoken')
        data = {'username': username, 'password': password,
                'csrfmiddlewaretoken': token}
        login = self.session.post(url, data=data, cookies=form.cookies,
                                  headers={'Referer': url})
        self.cookies = login.cookies

    def upload(self, filename):
        url = 'https://bitbucket.org/' + self.repository + '/downloads'
        s3_url = 'https://bbuseruploads.s3.amazonaws.com/'
        fields = ('acl', 'success_action_redirect', 'AWSAccessKeyId',
                  'Policy', 'Signature', 'Content-Type', 'key')
        form = self.session.get(url, cookies=self.cookies)
        data = odict((f, self._find_field(form.content, f)) for f in fields)
        basename = os.path.basename(filename)
        data['Content-Type'] = mimetypes.guess_type(filename)[0]
        data['key'] += basename
        class FoolishHack(object):
            """requests doesn't maintain form fields' order, so we have to
            do workaround it.  Works with requests==0.10.8"""
            def __init__(self, odict):
                self.odict = odict
            def copy(self):
                return self.odict
        with open(filename, 'rb') as fp:
            files = {'file': (basename, fp)}
            self.session.post(s3_url, data=FoolishHack(data), files=files)
        return url + '/' + basename

    def _find_field(self, form_string, name):
        pattern = (r'<input\s[^<>]*name=[\'"]' + re.escape(name) +
                   r'[\'"]\s[^>]*>')
        tag = re.search(pattern, form_string)
        token = re.search(r'value=[\'"]([^\'"]+)[\'"]', tag.group(0))
        return token.group(1)


if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-u', '--bb-username', dest='username',
                      help='Bitbucket username')
    parser.add_option('-p', '--bb-password', dest='password',
                      help='Bitbucket password')
    options, args = parser.parse_args()
    if len(args) > 1:
        parser.error('incorrect number of arguments')
    elif len(args) < 1:
        parser.error('require a filename')
    elif not options.username:
        parser.error('require -u/--bb-username option')
    elif not options.password:
        parser.error('require -p/--bb-password option')
    bb = BitbucketClient(options.username, options.password, 'dahlia/sider')
    bb.upload(args[0])

