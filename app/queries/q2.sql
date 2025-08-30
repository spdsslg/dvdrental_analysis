WITH
longer_than_60min AS (
    SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name,
        f.title
    FROM film f
    JOIN film_actor fa
    ON fa.film_id = f.film_id
    JOIN actor a
    ON a.actor_id = fa.actor_id
    WHERE length>60)

SELECT COUNT(*)
FROM longer_than_60min;