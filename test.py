import sqlite3

import pandas as pd

 

file_path = 'sample_datasets.xlsx' # INSERT YOUR FILE PATH TO "sample_datasets.xls" HERE

excel_data = pd.read_excel(file_path, sheet_name=None)

apps_df = excel_data['applications'].drop(columns=['Unnamed: 0'])

cust_df = excel_data['customers'].drop(columns=['Unnamed: 0'])

store_df = excel_data['stores'].drop(columns=['Unnamed: 0'])

marketing_df = excel_data['marketing'].drop(columns=['Unnamed: 0'])

 

# Create an SQLite database in memory (or you can use a file on disk like 'mydb.db')

conn = sqlite3.connect(':memory:')  # Use ':memory:' for an in-memory database

 

# Write the DataFrames to the SQLite database

apps_df.to_sql('applications', conn, index=False, if_exists='replace')

cust_df.to_sql('customers', conn, index=False, if_exists='replace')

store_df.to_sql('stores', conn, index=False, if_exists='replace')

marketing_df.to_sql('marketing', conn, index=False, if_exists='replace')

 

# Now you can run SQL queries on these tables. For example:

# Prompt 1: The marketing organization is curious to see what the cash used amount is for each campaign.

 
# Cash used amount per campaign

query = """
SELECT marketing.name AS campaign_name,
        SUM(applications.dollars_used) AS cash_used_amount
FROM applications
JOIN customers ON applications.customer_id = customers.customer_id
JOIN marketing ON customers.campaign = marketing.id
GROUP BY marketing.name
ORDER BY cash_used_amount DESC;


-- WRITE SQL CODE HERE USING TABLE NAMES (customers, applications, stores, marketing)

"""

 

result = pd.read_sql(query, conn)

print(result)