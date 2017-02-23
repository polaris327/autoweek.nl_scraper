import time
import requests
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver


DOMAIN_NAME = 'http://www.autoweek.nl'
URL_PATTERN = 'http://www.autoweek.nl/autonieuws?page=%s'
NEWSITEM_PATTERN = 'newsitem-%s'


def get_article_links(last_article_date=None, limited=False):
    index = 1
    result = list()
    all_articles_found = False

    while(True):
        print 'Pages found: ', index
        page_html = requests.get(URL_PATTERN % index).text
        soup = BeautifulSoup(page_html, "html5lib")

        for x in xrange(20):
            try:
                raw_date = soup.find("div", {"id": NEWSITEM_PATTERN % x}) \
                               .find('div', {'class': "col item-meta2"}) \
                               .text.split('\n')[-2].split('\t')[-1]
                date = datetime.datetime.strptime(raw_date, '%Y-%m-%d')

                href = soup.find("div", {"id": NEWSITEM_PATTERN % x}).find('a')['href']
                result.append(DOMAIN_NAME + href)

                if last_article_date and date.date() < last_article_date.date():
                    all_articles_found = True
                    break
            except AttributeError:
                pass

        last_index = int(soup.findAll('a', {'class': 'button-tertiary'})[-1].text)
        if (last_index == index) or limited or all_articles_found:
            break

        index += 1

    print "Fetched %s article links" % len(result)
    return result


def get_articles(url_list):
    driver = webdriver.Firefox()
    date_crawled = datetime.datetime.now()
    article_list = list()

    for i, url in enumerate(url_list):
        print ' -- links performed: %s/%s' % (i, len(url_list))
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html5lib')
        try:
            try:
                author = soup.find('a', {'rel': 'author'}).text
            except:
                author = soup.find('div', {'class': 'article-meta'}).find('li').text

            title = soup.find('div', {"class": "contents widget"}).find('h1').text + '. ' + \
                    soup.find('div', {"class": "contents widget"}).find('h2').text
            intro = [soup.find('div', {"class": "contents widget"}).find('div', {"class": "intro"}).text]
            raw_paragraphs = soup.find('div', {"class": "contents widget"}).findAll('p')
            paragraphs_html = [str(x) for x in raw_paragraphs]
            article_html = str(soup.find('div', {"class": "intro"})) + ' ' + ' '.join(paragraphs_html)
            paragraphs = [x.text for x in raw_paragraphs]
            text = ' '.join(intro + paragraphs)
            images = [x['src'] for x in soup.findAll('img', {"class": "rsImg"})]
            date_published = soup.find('time')['datetime']

            raw_comments = soup.findAll('article', {"class": "comment"})
            comments = list()
        except Exception as e:
            print "BS parsing problem"

        for raw_comment in raw_comments:
            comment_author = raw_comment.find('a', {"class": "user-name"}).text
            text = raw_comment.find('p').text
            comment_date_published = raw_comment.find('time')['datetime']
            comments.append({
                'source': 'Autoweek',
                'author': comment_author,
                'datepublished': comment_date_published,
                'text': text,
                'crawldate': date_crawled
            })

        article_list.append({
            "url": url,
            'source': 'Autoweek',
            'title': title,
            'text': text,
            'html': article_html,
            'imageurl': images[0],
            'author': author,
            'datepublished': date_published,
            'crawldate': date_crawled,
            'comments': comments
        })

    driver.close()
    print "Fetched articles"
    return article_list
