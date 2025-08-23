SELECT a.actor_id,
        CONCAT(a.first_name, ' ', a.last_name) AS full_name,
        COUNT(*) AS cnt
FROM actor a
JOIN film_actor fa
  ON a.actor_id = fa.actor_id
JOIN film f
  ON f.film_id = fa.film_id
GROUP BY a.actor_id,full_name
ORDER BY cnt DESC LIMIT 1;