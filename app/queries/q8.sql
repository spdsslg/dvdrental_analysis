WITH top_ten AS (
    SELECT c.customer_id,
            CONCAT(c.first_name,' ',c.last_name) AS full_name,
            SUM(p.amount) AS total
    FROM customer c
    JOIN payment p ON p.customer_id = c.customer_id
    GROUP BY c.customer_id, full_name
    ORDER BY total DESC
    LIMIT 10
    )

SELECT DATE_TRUNC('month', p.payment_date)::date AS pay_mon,
        tt.full_name,
        COUNT(*) AS pay_countpermon,
        SUM(p.amount) AS pay_amount
FROM top_ten tt
JOIN payment p 
  ON p.customer_id = tt.customer_id
WHERE p.payment_date >= '2007-01-01'
      AND p.payment_date <  '2008-01-01'
GROUP BY tt.customer_id, tt.full_name, pay_mon
ORDER BY full_name, pay_mon;