# base
import datetime
import hashlib
import json
import os
import re
import time

# from system
from distutils.version import LooseVersion

# 3rd-party
import requests
from bs4 import BeautifulSoup

def json_file_cache(fn):
    def wrapped(*args, **kwargs):
        fname = os.path.join(os.path.dirname(__file__), fn.__name__ + '_cache.json')
        if os.path.exists(fname) and int(time.time()) - int(os.path.getmtime(fname)) < 86400:
            result = json.loads(open(fname, 'r').read())
        else:
            result = fn(*args, **kwargs)
            if result:
                with open(fname, 'w') as dest:
                    dest.write(json.dumps(result))
        return result
    return wrapped

def matcher(s):
    os = hostname = kernel = ''
    match = re.match('^(Linux|Darwin)\s(?:(\S+)\s)(.+)\s(#(?:.+)|Darwin\sKernel\s(?:.+))$', s)
    if match and len(match.groups()) >= 3:
        os, hostname, kernel = match.groups()[0], match.groups()[1], match.groups()[2]
    return os, hostname, kernel

@json_file_cache
def get_kernels(somearg):
    url = 'https://www.kernel.org/'
    data = requests.get(url).text
    soup = BeautifulSoup(''.join(data), 'html.parser')
    versions = []
    for table in soup.find_all(lambda tag: tag.name == 'table' and tag.get('id') == 'releases'):
        # first table
        elements = table.find_all(lambda tag: tag.name == 'td' and tag.text.strip() != '' and not tag.text.startswith('['))
        for element in elements:
            if not element.text in ['mainline:', 'stable:', 'longterm:']:
                continue
            el = element
            ver = element.find_next_sibling()
            dat = ver.find_next_sibling()
            versions.append({'type': el.text.replace(':', ''),
                             'version': ver.text,
                             'date': dat.text})
        break
    return versions

def prepare_message(kernel_message):
    message = ''
    os, hostname, kernel = matcher(kernel_message)
    if not os or not hostname or not kernel:
        return message
    versions =  sorted(get_kernels('sss'), key=lambda item: LooseVersion(item.get('version')))
    for idx, version in enumerate(versions):
        date = version.get('date')
        comparable = version.get('version').split(' ')[0]
        if LooseVersion(comparable) >= LooseVersion(kernel):
            message = 'Your kernel {0!s} is at least {1!s} day(s) old, you should upgrade to {2!s} that was released at {3!s}'
            age = datetime.datetime.utcnow() - datetime.datetime.strptime(date, '%Y-%m-%d')
            age = age.days
            message = message.format(kernel, age, comparable, version.get('date'))
            break
    return message
