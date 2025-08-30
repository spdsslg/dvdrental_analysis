WITH 
actors_film_info AS (
    SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name,
        f.title,
        f.description,
        f.length
    FROM actor a
    JOIN film_actor fa
    ON a.actor_id = fa.actor_id
    JOIN film f
    ON f.film_id = fa.film_id)

SELECT COUNT(*)
FROM actors_film_info;