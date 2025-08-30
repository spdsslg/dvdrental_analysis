SELECT (CASE WHEN f.length<=60 THEN 1 
                WHEN f.length<=120 THEN 2
                WHEN f.length<=180 THEN 3
                ELSE 4 END) AS filmlen_groups,
            COUNT(*) AS films_in_a_group

FROM film f
GROUP BY filmlen_groups
ORDER BY filmlen_groups;