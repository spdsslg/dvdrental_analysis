SELECT inv.store_id,
       DATE_TRUNC('month',r.rental_date) AS rental_month,
	   COUNT(*) AS Count_rentals
FROM inventory inv
JOIN rental r
ON inv.inventory_id = r.inventory_id
GROUP BY inv.store_id, DATE_TRUNC('month',r.rental_date)
ORDER BY rental_month,inv.store_id 