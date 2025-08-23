WITH 
    top_ten AS (
        SELECT c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) AS full_name,
            SUM(amount) AS total
        FROM customer c
        JOIN payment p
        ON p.customer_id = c.customer_id
        GROUP BY c.customer_id, full_name
        ORDER BY total DESC LIMIT 10
    ),
    rent_info_top_10 AS (
        SELECT DATE_TRUNC('month',p.payment_date) AS pay_mon,
            tt.full_name,
            SUM(p.amount) AS pay_amount
        FROM  top_ten tt
        JOIN payment p
        ON p.customer_id = tt.customer_id
        WHERE p.payment_date >= '2007-01-01' AND p.payment_date<'2008-01-01'
        GROUP BY tt.customer_id, tt.full_name, pay_mon
        ORDER BY full_name,pay_mon
    )

SELECT pay_mon,
        full_name,
        pay_amount,
        LAG(pay_amount,1,0) OVER (PARTITION BY full_name ORDER BY pay_mon) AS prev_month_pay,
        pay_amount - LAG(pay_amount,1,0) OVER (PARTITION BY full_name ORDER BY pay_mon) AS monthly_diff_lag
FROM rent_info_top_10