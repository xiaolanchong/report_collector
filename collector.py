import re
import typing
import vk_api
import pprint
import time
import datetime
import sqlite3
from collections import namedtuple


Post = namedtuple('Post', 'post_id owner_id is_group name screen_name time hash_tags')
re_tag = re.compile(r'#не\w+нять_порачитать_(\w+)', re.UNICODE | re.IGNORECASE)


def to_timestamp(dt: datetime.datetime) -> int:
    ts = time.mktime(dt.timetuple())
    return int(ts)


def request_posts(vk: vk_api.VkApi, from_time: datetime.datetime, to_time: datetime.datetime, query: str):
    try:
        from_ts = to_timestamp(from_time)
        to_ts = to_timestamp(to_time)
        start_from = None
        have_more = True
        all_items = []
        user_id_to_name = {}
        group_id_to_name = {}
        while have_more:
            # see args at https://dev.vk.com/method/newsfeed.get
            response = vk.newsfeed.search(q=query, filter=['post'], extended=1,
                                          count=50, fields=['screen_name'],
                                          start_time=from_ts, end_time=to_ts, start_from=start_from)
            for group in response['groups']:
                group_id_to_name[group['id']] = (group['name'], group['screen_name'])
            for user in response['profiles']:
                user_id_to_name[user['id']] = (user['first_name'] + ' ' + user['last_name'], user['screen_name'])
            start_from = response.get('next_from')
            have_more = start_from is not None
            all_items.extend(response['items'])
            print(f"fetched {len(response['items'])} posts")
        return all_items, user_id_to_name, group_id_to_name
    except vk_api.VkApiError as error:
        print(error)
        return None, None, None


def get_hash_tags(text: str):
    return re_tag.findall(text)


def get_posts(vk, from_time: datetime.datetime, to_time: datetime.datetime, query: str) -> typing.List[Post]:
    posts = []
    post_items, user_id_to_names, group_id_to_names = request_posts(vk, from_time, to_time, query)
    for item in post_items:
        post_id = item['id']
        owner_id = item['owner_id']
        when = datetime.datetime.fromtimestamp(item['date'])
        text = item['text']
        name, screen_name = group_id_to_names.get(abs(owner_id), ('NOT FOUND', 'NOT FOUND')) \
            if owner_id < 0 else user_id_to_names.get(owner_id, ('NOT FOUND', 'NOT FOUND'))
        hash_tags = get_hash_tags(text)
        posts.append(Post(post_id=post_id, owner_id=abs(owner_id), is_group=owner_id < 0,
                          name=name, screen_name=screen_name, time=when, hash_tags=hash_tags))
    return posts


def import_to_table(filename: str, posts: typing.List[Post]):
    with sqlite3.connect(filename) as con:
        cur = con.cursor()
        for post in posts:
            try:
                cur.execute('insert into user (id, name, screen_name, is_group) values (?, ?, ?, ?)',
                            (post.owner_id, post.name, post.screen_name, 1 if post.is_group else 0))
            except sqlite3.IntegrityError:
                pass
            try:
                str_time = post.time.strftime('%Y-%m-%d %H:%M:%S')
                cur.execute('insert into post (id, user_id, time) values(?, ?, ?)',
                            (post.post_id, post.owner_id, str_time))
            except sqlite3.IntegrityError:
                pass
            for tag in post.hash_tags:
                cur.execute('insert into hash_tag (post_id, user_id, tag) values(?, ?, ?)',
                            (post.post_id, post.owner_id, tag))


def main():
    access_token = open('access_token.txt').read()
    session = vk_api.VkApi(token=access_token, api_version='5.131')
    vk = session.get_api()

    #from_time = datetime.datetime.now() - datetime.timedelta(days=10)
    from_time = datetime.datetime(2021, 1, 1)
    #to_time = datetime.datetime.now()
    to_time = datetime.datetime(2021, 3, 23)
    tag = '#некогдаобъяснять_порачитать'
    posts = get_posts(vk, from_time, to_time, tag)
    import_to_table('../report_collector.db', posts)
    #pprint.pprint(posts)


main()
