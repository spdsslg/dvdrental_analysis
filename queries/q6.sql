WITH quartile AS (
    SELECT c.name AS category,
            NTILE(4) OVER (ORDER BY f.rental_duration, f.film_id) AS percentile
    FROM film f
    JOIN film_category fc
        ON fc.film_id = f.film_id
    JOIN category c
        ON c.category_id = fc.category_id
    )

SELECT q.category,
       q.percentile,
       COUNT(*) AS cnt
FROM quartile q
WHERE q.category IN ('Animation','Children','Classics','Comedy','Family','Music')
GROUP BY q.category, q.percentile
ORDER BY q.category, q.percentile