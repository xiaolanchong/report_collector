-- script to get users sumbit the most number of messages
select screen_name, user.name, count(post.id) as num from post
inner join user on user.id = post.user_id
group by post.user_id
order by num desc
