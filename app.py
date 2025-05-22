# Imports
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuruation
st.set_page_config(
    page_title="BI Engineer Tech Assessment",
    page_icon="📊",
    layout="wide"
)

view = st.sidebar.selectbox(
    "Select View",
    ("Tasks 1-3", "Task 4", "Task 5")
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            min-width: 160px !important;
            max-width: 160px !important;
            width: 160px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load and cache the data
@st.cache_data
def load_data():
    applications_df = pd.read_excel('sample_datasets.xlsx', sheet_name='applications')
    #customers_df = pd.read_excel('sample_datasets.xlsx', sheet_name='customers')
    #stores_df = pd.read_excel('sample_datasets.xlsx', sheet_name='stores')
    marketing_df = pd.read_excel('sample_datasets.xlsx', sheet_name='marketing')
    return applications_df, marketing_df

applications_df, marketing_df = load_data()



# Task 1 ------------------------------------------------------------------------------------------------------------
if view == "Tasks 1-3":

    # Calculate the number of applications
    applications_count = len(applications_df)
    st.header("Task 1")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total applications", f"{applications_count:,}")

    # Calculate the number of approved applications
    approved_applications_df = applications_df[applications_df['approved'] == True]
    approved_count = len(approved_applications_df)
    with col2:
        st.metric("Approved applications", f"{approved_count:,}")

    # Calculate the number of used applications
    used_applications_df = applications_df[applications_df['dollars_used'] > 0]
    used_count = len(used_applications_df)
    with col3:
        st.metric("Used applications", f"{used_count:,}")

    # Visulaize the trend over the submission date
    applications_df['submit_date'] = pd.to_datetime(applications_df['submit_date'])
    applications_df['submit_month'] = applications_df['submit_date'].dt.to_period('M')
    applications_df['submit_month'] = applications_df['submit_month'].dt.to_timestamp()

    # Number of applications per month
    applications_per_month = applications_df.groupby('submit_month').size().reset_index(name='num_applications')

    # Number of approved applications per month
    approved_per_month = applications_df[applications_df['approved'] == True].groupby('submit_month').size().reset_index(name='num_approved')

    # Number of used applications per month
    used_per_month = applications_df[applications_df['dollars_used'] > 0].groupby('submit_month').size().reset_index(name='num_used')

    # Individual plots (Decided to stick with these as the scale for the combined plot makes it difficult to compare trends)
    fig_applications = px.line(
        applications_per_month,
        x='submit_month',
        y='num_applications',
        title='Number of Applications Over Time',
        labels={'submit_month': 'Submission Month', 'num_applications': 'Number of Applications'},
    )
    fig_applications.update_layout(hovermode='x unified')
    st.write(fig_applications)

    fig_approved = px.line(
        approved_per_month,
        x='submit_month',
        y='num_approved',
        title='Number of Approved Applications Over Time',
        labels={'submit_month': 'Submission Month', 'num_approved': 'Number of Approved Applications'},
    )
    fig_approved.update_traces(line_color='lightgreen')
    fig_approved.update_layout(hovermode='x unified')
    st.write(fig_approved)

    fig_used = px.line(
        used_per_month,
        x='submit_month',
        y='num_used',
        title='Number of Used Applications Over Time',
        labels={'submit_month': 'Submission Month', 'num_used': 'Number of Used Applications'},
    )
    fig_used.update_layout(hovermode='x unified')
    fig_used.update_traces(line_color='blue')
    st.write(fig_used)




    # Task 2 ------------------------------------------------------------------------------------------------------------
    st.header("Task 2")

    col1, col2 = st.columns(2)
    # Calculate the average of the approved amount, and avgerage per month (excluding None or blank)
    avg_approved = applications_df['approved_amount'].mean()
    avg_approved_per_month = applications_df.groupby('submit_month')['approved_amount'].mean().reset_index(name='avg_approved_amount')
    with col1:
        st.metric("Average approved amount", f"${avg_approved:,.2f}")

    # Calculate the average of the used amount and average per month (excluding None or blank)
    avg_used = applications_df['dollars_used'].mean()
    avg_used_per_month = applications_df.groupby('submit_month')['dollars_used'].mean().reset_index(name='avg_used_amount')
    with col2:
        st.metric("Average used amount", f"${avg_used:,.2f}")

    # Visualize the trend over the submission date

    #Plot average approved amount per month
    fig_avg_approved = px.line(
        avg_approved_per_month,
        x='submit_month',
        y='avg_approved_amount',
        title='Average Approved Amount Per Month',
        labels={'submit_month': 'Submission Month', 'avg_approved_amount': 'Average Approved Amount ($)'},
    )
    fig_avg_approved.update_yaxes(tickprefix="$", tickformat=",")
    fig_avg_approved.update_traces(line_color='teal')
    fig_avg_approved.update_layout(hovermode='x unified')
    st.write(fig_avg_approved)

    # Plot average used amount per month
    fig_avg_used = px.line(
        avg_used_per_month,
        x='submit_month',
        y='avg_used_amount',
        title='Average Used Amount Per Month',
        labels={'submit_month': 'Submission Month', 'avg_used_amount': 'Average Used Amount ($)'},
    )
    fig_avg_used.update_yaxes(tickprefix="$", tickformat=",")
    fig_avg_used.update_traces(line_color='lightpink')
    fig_avg_used.update_layout(hovermode='x unified')
    st.write(fig_avg_used)




    # Task 3 ------------------------------------------------------------------------------------------------------------
    st.header("Task 3")
    st.subheader("Metrics by Store")
    # Create a table to show possible metrics (e.g. number of applications, number of approved, approved amount, number of used, used amount, percentages, etc) by store.

    # Create dataframe for metrics by store
    summary = applications_df.groupby('store')['application_id'].nunique().reset_index(name='total_applications')

    approved_summary_df = approved_applications_df.groupby('store').agg(
        num_approved_applications=('application_id', 'nunique'),
        total_approved_amount=('approved_amount', 'sum'),
    ).reset_index()

    used_summary_df = used_applications_df.groupby('store').agg(
        num_used_applications=('application_id', 'nunique'),
        total_used_amount=('dollars_used', 'sum'),
    ).reset_index()

    store_summary_df = summary \
        .merge(approved_summary_df, on='store', how='left') \
        .merge(used_summary_df, on='store', how='left') \
        .fillna(0)

    # Clean and order 'store' column 
    store_summary_df['store'] = store_summary_df['store'].str.replace('store_', '', regex=False).astype(int)
    store_summary_df = store_summary_df.sort_values(by='store', ascending=True)

    # Calculate percentages
    store_summary_df['percent_of_funds_used'] = (store_summary_df['total_used_amount'] / store_summary_df['total_approved_amount'] * 100)
    store_summary_df['percent_of_apps_approved'] = (store_summary_df['num_approved_applications'] / store_summary_df['total_applications'] * 100)
    store_summary_df['percent_of_apps_used'] = (store_summary_df['num_used_applications'] / store_summary_df['total_applications'] * 100)

    # Reorder the columns for display
    store_summary_df_column_order = [
        'store',
        'total_applications',
        'num_approved_applications',
        'num_used_applications',
        'percent_of_apps_approved',
        'percent_of_apps_used',
        'total_approved_amount',
        'total_used_amount',
        'percent_of_funds_used'
    ]
    store_summary_df = store_summary_df[store_summary_df_column_order]

    # Define custom column names for display
    column_names = [
        "Store",
        "Total Applications",
        "Approved Applications",
        "Used Applications",
        "% Applications Approved",
        "% Applications Used",
        "Total Approved Amount",
        "Total Used Amount",
        "% Funds Used"
    ]

    # Format percentage columns to two decimal places and add '%'
    percent_cols = [
        'percent_of_apps_approved',
        'percent_of_apps_used',
        'percent_of_funds_used'
    ]

    for col in percent_cols:
        store_summary_df[col] = store_summary_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

    # Format the columns to show as currency
    currency_cols = [
        'total_approved_amount',
        'total_used_amount'
    ]

    for col in currency_cols:
        store_summary_df[col] = store_summary_df[col].apply(lambda x: f"${x:,}" if pd.notnull(x) else "")


    table = go.Figure(data=[
        go.Table(
            header=dict(
                values=column_names,
                align='left',
                font=dict(size=16, color='white'),
                fill_color='darkslategray',
                height=45
            ),
            cells=dict(
                values=[store_summary_df[col] for col in store_summary_df.columns],
                align='left',
                font=dict(size=14),
                height=32
            )
        )
    ])
    # Set a larger height for the table to show more rows and enable vertical scrolling if needed
    table.update_layout(
        autosize=True,
        height=800,  # Increase this value as needed to show more rows
        margin=dict(l=0, r=0, t=10, b=0)
    )

    st.write(table)




# Task 4 ------------------------------------------------------------------------------------------------------------
if view == "Task 4":
    st.header("Task 4")

    # Clean the marketing dataframe
    marketing_df = marketing_df.iloc[1:].reset_index(drop=True)

    # Create a view with a graph to compare the used dollars amount by marketing name, and color by spend amount
    
    # Sort the marketing_df by 'spend' in descending order before plotting
    marketing_df_sorted = marketing_df.sort_values(by='spend', ascending=False)

    fig_marketing = px.bar(
        marketing_df_sorted,
        x='name',
        y='spend',
        color='spend',
        title='Used Dollars Amount by Marketing Name',
        labels={'name': 'Marketing Name', 'spend': 'Used Dollars Amount ($)'},
    )
    fig_marketing.update_yaxes(tickprefix="$")
    st.write(fig_marketing)




# Task 5 ------------------------------------------------------------------------------------------------------------
if view == "Task 5":
    st.header("Task 5 - Outliers based on Store metrics")

    # Recreate the store summary dataframe for Task 5
    approved_applications_df = applications_df[applications_df['approved'] == True]
    used_applications_df = applications_df[applications_df['dollars_used'] > 0]

    summary = applications_df.groupby('store')['application_id'].nunique().reset_index(name='total_applications')

    approved_summary_df = approved_applications_df.groupby('store').agg(
        num_approved_applications=('application_id', 'nunique'),
        total_approved_amount=('approved_amount', 'sum'),
    ).reset_index()

    used_summary_df = used_applications_df.groupby('store').agg(
        num_used_applications=('application_id', 'nunique'),
        total_used_amount=('dollars_used', 'sum'),
    ).reset_index()

    store_summary_df = summary \
        .merge(approved_summary_df, on='store', how='left') \
        .merge(used_summary_df, on='store', how='left') \
        .fillna(0)

    store_summary_df['store'] = store_summary_df['store'].str.replace('store_', '', regex=False).astype(int)
    store_summary_df = store_summary_df.sort_values(by='store', ascending=True)

    store_summary_df['percent_of_funds_used'] = (store_summary_df['total_used_amount'] / store_summary_df['total_approved_amount'] * 100)
    store_summary_df['percent_of_apps_approved'] = (store_summary_df['num_approved_applications'] / store_summary_df['total_applications'] * 100)
    store_summary_df['percent_of_apps_used'] = (store_summary_df['num_used_applications'] / store_summary_df['total_applications'] * 100)

    store_summary_df_column_order = [
        'store',
        'total_applications',
        'num_approved_applications',
        'num_used_applications',
        'percent_of_apps_approved',
        'percent_of_apps_used',
        'total_approved_amount',
        'total_used_amount',
        'percent_of_funds_used'
    ]
    store_summary_df = store_summary_df[store_summary_df_column_order]

    percent_cols = [
        'percent_of_apps_approved',
        'percent_of_apps_used',
        'percent_of_funds_used'
    ]
    for col in percent_cols:
        store_summary_df[col] = store_summary_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

    currency_cols = [
        'total_approved_amount',
        'total_used_amount'
    ]
    for col in currency_cols:
        store_summary_df[col] = store_summary_df[col].apply(lambda x: f"${x:,}" if pd.notnull(x) else "")

    # Let's see if there are any outliers in stores approving applications

    # Clean 'total_approved_amount' for numeric calculations
    store_summary_df['total_approved_amount_numeric'] = (
        store_summary_df['total_approved_amount']
        .replace('[\$,]', '', regex=True)
        .astype(float)
    )

    # Calculate the IQR for the total approved amount
    Q1 = store_summary_df['total_approved_amount_numeric'].quantile(0.25)
    Q3 = store_summary_df['total_approved_amount_numeric'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = store_summary_df[
        (store_summary_df['total_approved_amount_numeric'] < lower_bound) | 
        (store_summary_df['total_approved_amount_numeric'] > upper_bound)
    ]


    st.header("Outliers in Total Approved Amount")
    for store in outliers['store']:
        st.subheader(f"Store #{store}")
        st.metric(f"Store {store} has an outliter in total approved amount", f"{outliers[outliers['store'] == store]['total_approved_amount'].values[0]}")


    # Let's see if there are any outliers in the percent of funds used

    # Clean 'percent_of_funds_used' for numeric calculations
    store_summary_df['percent_of_funds_used_numeric'] = (
        store_summary_df['percent_of_funds_used']
        .replace('[\%,]', '', regex=True)
        .astype(float)
    )

    # Calculate the IQR for the percent of funds used
    Q1 = store_summary_df['percent_of_funds_used_numeric'].quantile(0.25)
    Q3 = store_summary_df['percent_of_funds_used_numeric'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = store_summary_df[
        (store_summary_df['percent_of_funds_used_numeric'] < lower_bound) | 
        (store_summary_df['percent_of_funds_used_numeric'] > upper_bound)
    ]


    st.header("Outliers in Percent of Funds Used")
    for store in outliers['store']:
        st.subheader(f"Store #{store}")
        st.metric(f"Store {store} has an outlier in percent of funds used", f"{outliers[outliers['store'] == store]['percent_of_funds_used'].values[0]}")



# These are included for viewing. Uncomment to see the dataframe in the browser

# st.write(applications_df)
# st.write(customers_df)
# st.write(stores_df)
# st.write(marketing_df)