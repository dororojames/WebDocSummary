from __future__ import unicode_literals
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
from .utils import _get_search_url, get_html
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import unquote, parse_qs, urlparse
from unidecode import unidecode
from re import match, findall


class GoogleResult(object):

    """Represents a google search result."""

    def __init__(self):
        self.name = None  # The title of the link
        self.link = None  # The external link
        self.description = None  # The description of the link
        self.page = None  # Results page this one was on
        self.index = None  # What index on this page it was on

    def __repr__(self):
        name = self._limit_str_size(self.name, 55)
        description = self._limit_str_size(self.description, 49)

        list_google = ["GoogleResult(",
                       "name={}".format(name), "\n", " " * 13,
                       "description={}".format(description)]

        return "".join(list_google)

    def _limit_str_size(self, str_element, size_limit):
        """Limit the characters of the string, adding .. at the end."""
        if not str_element:
            return None

        elif len(str_element) > size_limit:
            return unidecode(str_element[:size_limit]) + ".."

        else:
            return unidecode(str_element)


# PUBLIC
def search(query, goal_num=30, pages=3, lang='en', void=True):
    """Returns a list of GoogleResult.

    Args:
        query: String to search in google.
        pages: Number of pages where results must be taken.
        area : Area of google homepages.

    TODO: add support to get the google results.
    Returns:
        A GoogleResult object."""

    results = []
    for i in range(pages):
        url = _get_search_url(query, i, lang=lang)
        html = get_html(url)

        if html:
            soup = BeautifulSoup(html, "html.parser")
            divs = soup.findAll("div", attrs={"class": "g"})

            j = 0
            for li in divs:
                res = GoogleResult()

                res.page = i
                res.index = j

                res.name = _get_name(li)
                res.link = _get_link(li)
                res.description = _get_description(li)

                if void is True:
                    if res.description is None:
                        continue
                if selected(res):
                    # res.html = get_html(res.link)
                    results.append(res)
                if len(results) == goal_num:
                    return results
                j += 1
    return results


# PRIVATE
def _get_name(li):
    """Return the name of a google search."""
    a = li.find("h3")
    # return a.text.encode("utf-8").strip()
    if a is not None:
        return a.text.strip()
    return None


def _filter_link(link):
    '''Filter links found in the Google result pages HTML code.
    Returns None if the link doesn't yield a valid result.
    '''
    try:
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        # link type-1
        # >>> "https://www.gitbook.com/book/ljalphabeta/python-"
        if o.netloc and 'google' not in o.netloc:
            return link
        # link type-2
        # >>> "http://www.google.com/url?url=http://python.jobbole.com/84108/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggUMAA&usg=AFQjCNHPws5Buru5Z71wooRLHT6mpvnZlA"
        if o.netloc and o.path.startswith('/url'):
            try:
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                pass
        # Decode hidden URLs.
        if link.startswith('/url?'):
            try:
                # link type-3
                # >>> "/url?q=http://python.jobbole.com/84108/&sa=U&ved=0ahUKEwjFw6Txg4_UAhVI5IMKHfqVAykQFggUMAA&usg=AFQjCNFOTLpmpfqctpIn0sAfaj5U5gAU9A"
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                # link type-4
                # >>> "/url?url=https://machine-learning-python.kspax.io/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggfMAI&usg=AFQjCNEfkUI0RP_RlwD3eI22rSfqbYM_nA"
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None


def _get_link(li):
    """Return external link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except Exception:
        return None
    return _filter_link(link)


def _get_description(li):
    """Return the description of a google search.

    TODO: There are some text encoding problems to resolve."""

    sdiv = li.find("div", attrs={"class": "s"})
    if sdiv:
        stspan = sdiv.find("span", attrs={"class": "st"})
        if stspan is not None:
            # return stspan.text.encode("utf-8").strip()
            return stspan.text.strip()
    else:
        return None


def _get_thumb():
    """Return the link to a thumbnail of the website."""
    pass


bandword = ["ppt", "slide", "news", "tv",
            "facebook", "平台", "平臺", "book", "course", "課程"]


def selected(res):
    if res.link == None:
        print("reslink is None")
        return False
    for bw in bandword:
        if bw in res.name or bw in res.link:
            return False
    return True
