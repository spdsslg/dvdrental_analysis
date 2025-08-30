WITH temp AS(
    SELECT f.title,
            c.name AS category,
            COUNT(r.rental_id) AS cnt
    FROM film f
    JOIN film_category fc
      ON f.film_id = fc.film_id
    JOIN category c
      ON c.category_id = fc.category_id 
      AND (c.name = 'Animation' OR c.name = 'Children' OR c.name = 'Classics' OR c.name = 'Comedy' 
      OR c.name = 'Family' OR c.name = 'Music')
    LEFT JOIN inventory i
      ON i.film_id = f.film_id
    LEFT JOIN rental r
      ON r.inventory_id = i.inventory_id
    GROUP BY f.film_id, c.name,f.title
    ORDER BY category, f.title)

SELECT category,
    SUM(cnt) AS num_of_rentals
FROM temp
GROUP BY category
ORDER BY num_of_rentals DESC