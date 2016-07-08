import shutil
import urllib
import random
import requests
from bs4 import BeautifulSoup
from antigate import AntiGate


def hook_factory(query):
    def print_url(r, *args, **kwargs):
        if 'GOOGLE_ABUSE_EXEMPTION' in r.cookies:
            resp = requests.get('http://google.com/search',
                                params={'q': query},
                                headers={'User-agent': 'Mozilla/5.0'},
                                cookies={'GOOGLE_ABUSE_EXEMPTION': r.cookies['GOOGLE_ABUSE_EXEMPTION']})
            return resp
    return print_url


def crawl_google_pages(query):
    resp = requests.get('http://google.com/search',
                        params={'q': query},
                        headers={'User-agent': 'Mozilla/5.0'})

    if resp.status_code == 503:
        bs = BeautifulSoup(resp.text, 'lxml')

        img_url = 'http://ipv4.google.com' + bs.find('img')['src']

        req_img = requests.get(img_url,
                               headers={'User-agent': 'Mozilla/5.0'},
                               stream=True)

        with open('.captcha.jpeg', 'wb') as f:
            shutil.copyfileobj(req_img.raw, f)

        captcha = str(AntiGate('5fe97f0269baab13414a37f10e240925', '.captcha.jpeg'))
        print 'capcha:', captcha

        cookies = {'GOOGLE_ABUSE_EXEMPTION': req_img.cookies['GOOGLE_ABUSE_EXEMPTION']}

        p = (('q', resp.url[resp.url.find('&q') + 3:]),
             ('continue', urllib.unquote(resp.url[resp.url.find('?continue') + 10:resp.url.find('&q')])),
             ('id', img_url[img_url.find('id') + 3:img_url.find('q') - 1]),
             ('captcha', captcha),
             ('submit', 'Submit'))

        resp = requests.get('http://ipv4.google.com/sorry/CaptchaRedirect',
                            params=p,
                            headers={'User-agent': 'Mozilla/5.0'},
                            cookies=cookies,
                            hooks={'response': [hook_factory(query=query)]})
    return resp


if __name__ == '__main__':
    pages = ['hallo+world', 'halo', 'hola', 'bla-bla-bla', 'qwerty', 'lalala', 'gsa', 'mint', 'turbo', 'python']
    #pages = ['hola', 'hallo+world']
    for _ in range(3):
        response = crawl_google_pages(random.choice(pages))
        print 'status:', response.status_code

        bs = BeautifulSoup(response.text, 'lxml')
        urls = bs.find_all('h3', 'r')
        print 'count url:', len(urls)
