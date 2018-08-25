# encoding=UTF-8

# Copyright © 2011, 2014 Jakub Wilk <jwilk@jwilk.net>

# Redistribution and use in source and compiled forms, with or without
# modification, are permitted under any circumstances. No warranty.

from __future__ import print_function

import os
import pipes
import subprocess as ipc

import apt_pkg

default_mirror = 'http://ftp.debian.org/debian'
default_distribution = 'unstable'

def setup_proxies():
    apt_pkg.init_config()
    os.environ['http_proxy'] = apt_pkg.config.get('Acquire::http::Proxy', '')
    os.environ['ftp_proxy'] = apt_pkg.config.get('Acquire::ftp::Proxy', '')

def setup_locale():
    os.environ['LC_ALL'] = 'C'

log_file = None

def setup_log_file(file):
    global log_file
    log_file = file

def log_download(url):
    print('D: {url}'.format(url=url), file=log_file)

def log_action(package, version, action):
    print(
        'I: {pkg} {ver} => {action}'.format(pkg=package, ver=version, action=action),
        file=log_file
    )

def log_error(package, version, message):
    print(
        'E: {pkg} {ver} => {message}'.format(pkg=package, ver=version, message=message),
        file=log_file
    )

class DownloadError(IOError):
    pass

class download:

    def __init__(self, url, pipe=None):
        self._url = url
        self._pipe = pipe

    def __enter__(self):
        log_download(self._url)
        quoted_url = pipes.quote(self._url)
        if self._url.startswith(('/', '.')):
            if self._pipe is not None:
                commandline = '< {url} {pipe}'.format(url=quoted_url, pipe=self._pipe)
            else:
                commandline = 'cat {url}'.format(url=quoted_url)
        else:
            commandline = 'wget -O- -q {url}'.format(url=quoted_url)
            if self._pipe is not None:
                commandline += ' | ' + self._pipe
        self._child = ipc.Popen(commandline, shell=True,
            stdout=ipc.PIPE, stderr=ipc.PIPE
        )
        return self._child.stdout

    def __exit__(self, exc_type, exc_val, exc_tb):
        stderr = self._child.stderr.read()
        if self._child.wait() != 0:
            stderr = stderr.decode('ASCII', 'replace').strip()
            raise DownloadError(stderr)

# vim:ts=4 sts=4 sw=4 et
