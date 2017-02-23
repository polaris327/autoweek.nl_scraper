from pymysql import err


def save_articles(connection, articles):
    for article in articles:
        try:
            sql = "INSERT INTO `articles` (`url`, `source`, `title`, `text`, `html`, `imageurl`, `author`, `datepublished`, `crawldate`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (article['url'], article['source'], article['title'], article['text'], article['html'], article['imageurl'], article['author'], article['datepublished'], article['crawldate']))
            article_id = cursor.lastrowid
            cursor.close()
        except err.IntegrityError:
            continue

        for comment in article['comments']:
            with connection.cursor() as cursor:
                comment.update({"id": article_id})
                sql = "INSERT INTO `article_comments` (`id_id`, `source`, `author`, `text`, `datepublished`, `crawldate`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (comment['id'], comment['source'], comment['author'], comment['text'], comment['datepublished'], comment['crawldate']))
                cursor.close()

        connection.commit()

    print "All articles saved"


def get_last_article_date(connection):
    with connection.cursor() as cursor:
        sql = "SELECT MAX(`datepublished`) as date FROM `articles`"
        cursor.execute(sql)
        result = cursor.fetchone()

    print 'Fetched last article date'
    return result['date']
