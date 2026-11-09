select cohort_month, months_since_first_purchase
from {{ ref('mart_customer_retention') }}
group by 1, 2
having count(*) > 1

