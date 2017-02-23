import sys
import pymysql.cursors


from db import save_articles, get_last_article_date
from scraper import get_article_links, get_articles


def fetch_all_articles(connection):
    article_url_list = get_article_links()
    articles = get_articles(article_url_list)
    save_articles(connection, articles)


def fetch_new_articles(connection):
    last_article_date = get_last_article_date(connection)
    article_url_list = get_article_links(last_article_date)

    if not article_url_list:
        print "New articles not found"
        return

    articles = get_articles(article_url_list)
    save_articles(connection, articles)


if __name__ == '__main__':
    connection = pymysql.connect(host='xxx',
                                 user='xxx',
                                 password='xxx',
                                 db='xxx',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    if len(sys.argv) == 2:
        if sys.argv[1] == '--full':
            fetch_all_articles(connection)
        elif sys.argv[1] == '--new':
            fetch_new_articles(connection)
        else:
            print "Unexpected parameter. Run the script again with --full or --new parameter"
    else:
        print "Unexpected parameter. Run the script again with --full or --new parameter"

    connection.close()
