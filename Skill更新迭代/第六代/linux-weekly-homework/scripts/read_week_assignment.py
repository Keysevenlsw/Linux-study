#!/usr/bin/env python3
"""Read one week's assignment from the course HTML/MHTML archive (stdlib only)."""

import argparse
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


def decode_html(data, mime_charset=None):
    meta = re.search(br'charset\s*=\s*["\x27]?([\w-]+)', data[:8192], re.I)
    encodings = [mime_charset, meta.group(1).decode('ascii') if meta else None,
                 'utf-8-sig', 'gb18030']
    for encoding in dict.fromkeys(x for x in encodings if x):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError('Cannot decode HTML without losing characters.')


def load_html(path):
    data = path.read_bytes()
    if path.suffix.lower() in ('.mhtml', '.mht'):
        message = BytesParser(policy=policy.default).parsebytes(data)
        pages = [decode_html(part.get_payload(decode=True), part.get_content_charset())
                 for part in message.walk() if part.get_content_type() == 'text/html']
        if not pages:
            raise ValueError('No HTML part in MHTML archive.')
        return next((page for page in pages if re.search(
            r'id\s*=\s*["\x27]article_content["\x27]', page, re.I)), pages[0])
    return decode_html(data)


class Article(HTMLParser):
    """Capture only the CSDN article container, excluding sidebars and comments."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth = 0
        self.found = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if not self.depth and not self.found and dict(attrs).get('id') == 'article_content':
            self.depth = 1
            self.found = True
            return
        if self.depth:
            if tag == 'div':
                self.depth += 1
            self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            if tag == 'div':
                self.depth -= 1
            if self.depth:
                self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data(f'&{name};')

    def handle_charref(self, name):
        self.handle_data(f'&#{name};')


class Text(HTMLParser):
    def __init__(self, links=True):
        super().__init__()
        self.parts = []
        self.links = links
        self.hrefs = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'li', 'br', 'div') or re.fullmatch(r'h[1-6]', tag):
            self.parts.append('\n')
        if tag == 'a':
            self.hrefs.append(dict(attrs).get('href', ''))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
        if tag in ('p', 'li', 'div') or re.fullmatch(r'h[1-6]', tag):
            self.parts.append('\n')
        if tag == 'a' and self.hrefs:
            href = self.hrefs.pop()
            if self.links and href.startswith(('https://', 'http://')):
                self.parts.append(f' ({href})')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def plain(fragment, links=True):
    parser = Text(links)
    parser.feed(fragment)
    return '\n'.join(re.sub(r'\s+', ' ', line).strip()
                     for line in ''.join(parser.parts).splitlines() if line.strip())


def week_number(label):
    match = re.fullmatch(r'第([一二三四五六七八九十两\d]+)周(?:作业)?', label)
    if not match:
        return None
    value = match.group(1)
    if value.isdigit():
        return int(value)
    digits = dict(zip('一二三四五六七八九', range(1, 10)))
    digits['两'] = 2
    if '十' in value:
        tens, ones = value.split('十')
        return digits.get(tens, 1) * 10 + digits.get(ones, 0)
    return digits.get(value)


def assignment_list(fragment):
    """Use the numbered task list, excluding promotions after the final week."""
    depth = 0
    start = None
    for tag in re.finditer(r'<(/?)ol\b[^>]*>', fragment, re.I):
        if not tag.group(1):
            if start is None:
                start = tag.start()
            depth += 1
        elif start is not None:
            depth -= 1
            if depth == 0:
                return fragment[start:tag.end()]
    raise ValueError('No complete numbered assignment list in the week section.')


def extract_week(html, week):
    article = Article()
    article.feed(html)
    fragment = ''.join(article.parts) if article.found else html
    headings = list(re.finditer(r'<h([1-6])\b[^>]*>(.*?)</h\1\s*>', fragment,
                                flags=re.I | re.S))
    for index, heading in enumerate(headings):
        label = plain(heading.group(2), links=False)
        if week_number(label) != week:
            continue
        end = len(fragment)
        for following in headings[index + 1:]:
            if int(following.group(1)) <= int(heading.group(1)):
                end = following.start()
                break
        lines = []
        tasks = assignment_list(fragment[heading.end():end])
        for line in plain(tasks).splitlines():
            if '豆列' in line or 'douban.com/doulist/' in line:
                continue
            line = re.sub(r'基于树莓派或其他平台完成\s*ARM\s*相关内容[。．.]?', '',
                          line, flags=re.I).strip()
            if line:
                lines.append(line)
        if not lines:
            raise ValueError(f'Week {week} heading found, but no assignment remains.')
        return f'# {label}\n\n' + '\n\n'.join(lines) + '\n'
    raise ValueError(f'No standalone week {week} assignment heading found.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--week', type=int, required=True)
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        print(extract_week(load_html(args.archive), args.week), end='')
    except (OSError, ValueError) as error:
        parser.exit(1, f'Assignment lookup failed: {error}\n')


if __name__ == '__main__':
    main()
