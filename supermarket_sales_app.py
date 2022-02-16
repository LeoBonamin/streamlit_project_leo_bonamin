from calendar import month_name
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title='Supermarket Sales Analysis',
    page_icon=':chart_with_upwards_trend:',
    layout="wide")

st.title('Supermarket Sales Analysis')
description = (
    "**This is an Intercative Dashboard:** Please select filters in the\
     left-hand panel to obtain insights according to chosen characteristics.")
st.markdown(description)

df = pd.read_csv(
    './supermarket_sales - Sheet1.csv'
)

# ------- Data Cleaning -------

# Rename columns
df.rename(columns={'Invoice ID': 'Invoice_ID'}, inplace=True)
df.rename(columns={'Customer type': 'Customer_type'}, inplace=True)
df.rename(columns={'Product line': 'Product_line'}, inplace=True)
df.rename(columns={'Unit price': 'Unit_price'}, inplace=True)
df.rename(
    columns={'gross margin percentage': 'gross_margin_percentage'},
    inplace=True)
df.rename(columns={'gross income': 'gross_income'}, inplace=True)

# Date type
df['Date'] = pd.to_datetime(df['Date'])

# New feature : Unit price with bins
unit_price_categories = df.assign(price_bins=pd.cut(
    df["Unit_price"], [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    labels=['0 to 10', '10 to 20', '20 to 30', '30 to 40', '40 to 50',
            '50 to 60', '60 to 70', '70 to 80', '80 to 90', '90 to 100']))

# Create new column with just month
df['month'] = pd.DatetimeIndex(df['Date']).month
df['month'] = df['month'].replace({1: 'January', 2: 'February', 3: 'March'})

# ------- Build filters -------
# Definition of the variables used in filters
city_list = df['City'].unique().tolist()
customer_type = df['Customer_type'].unique().tolist()
gender = df['Gender'].unique().tolist()
month = df['month'].unique().tolist()
month_lookup = list(month_name)

# Input widgets
st.sidebar.title('Select your filters')
city_selection = st.sidebar.multiselect(
    'Select a city',
    city_list,
    default=city_list)

customer_type_selection = st.sidebar.multiselect(
    'Select customer type',
    customer_type,
    default=customer_type)

gender_selection = st.sidebar.multiselect(
    'Select a gender',
    gender,
    default=gender)

date_selection = st.sidebar.select_slider(
    'Select a date',
    sorted(month, key=month_lookup.index))

# Link filters to data
df_selection = df.query(
    "City == @city_selection & Customer_type == @customer_type_selection\
    & Gender == @gender_selection & month == @date_selection"
)

# ------- Defintion of the variable to plot -------
total_sales_by_date = (
    df_selection.groupby(by=["Date"]).sum()[["Total"]]
)
total_sales_by_date = pd.DataFrame(total_sales_by_date)
total_sales_by_date.reset_index(inplace=True)

product_line_quantity = (
    df_selection.groupby(by=['Product_line']).sum([['Quantity']])
    .sort_values(by='Quantity', ascending=False)
)
product_line_quantity = pd.DataFrame(product_line_quantity)
product_line_quantity.reset_index(inplace=True)

product_line_total = (
    df_selection.groupby(by=['Product_line']).sum([['Total']])
    .sort_values(by='Total', ascending=False)
)
product_line_total = pd.DataFrame(product_line_total)
product_line_total.reset_index(inplace=True)

means_of_payment = (
    df_selection
)
means_of_payment = pd.DataFrame(means_of_payment)
means_of_payment.reset_index(inplace=True)

rating_evolution = (
    df_selection.groupby(by=["Date"]).mean()[["Rating"]]
)
rating_evolution = pd.DataFrame(rating_evolution)
rating_evolution.reset_index(inplace=True)

rating_date = (
    df_selection.groupby(by=["Date"]).mean()[["Rating"]]
)
rating_date = pd.DataFrame(rating_date)
rating_date.reset_index(inplace=True)

colors = ['#0e9aa7', '#f6cd61', '#fe8a71']
explode = (0.05, 0.05, 0.05)

# ------- Build the KPI's part -------
average_rating = round(df_selection['Rating'].mean(), 1)
average_unit_price = round(df_selection['Unit_price'].mean(), 1)
average_quantity_bought = round(df_selection['Quantity'].mean(), 1)
average_gross_income = round(df_selection['gross_income'].mean(), 1)
average_total = round(df_selection['Total'].mean(), 1)


def show_result_mgs(
        average_rating,
        average_unit_price,
        average_quantity_bought,
        average_total,
        average_gross_income
        ):
    st.markdown(f"**Avg. rating:** {average_rating:,} :star:")
    st.markdown(f"**Avg. unit price:** {average_unit_price:,} \U0001f4b2")
    st.markdown(f"**Avg. quantity:** {average_quantity_bought:,}")
    st.markdown(f"**Avg. total bought (Tax 5%):** {average_total:,}\
     \U0001f4b2")
    st.markdown(f"**Avg. gross income:** {average_gross_income:,}")

# ------- Build the plots -------
fig1, ax = plt.subplots()
ax.plot(total_sales_by_date['Date'], total_sales_by_date['Total'])
plt.xticks(rotation=45, ha='right')

fig2, ax = plt.subplots()
ax.bar(
    product_line_quantity['Product_line'],
    product_line_quantity['Quantity'],
    color='#0e9aa7')
plt.xticks(rotation=45, ha='right')

fig3, ax = plt.subplots()
ax.bar(
    product_line_total['Product_line'],
    product_line_total['Total'],
    color='#f6cd61')
plt.xticks(rotation=45, ha='right')

fig4, ax = plt.subplots()
ax.pie(
    means_of_payment['Payment'].value_counts(),
    labels=means_of_payment['Payment'].unique(),
    autopct='%1.0f%%',
    colors=colors,
    startangle=90,
    pctdistance=0.85,
    explode=explode,
    textprops={'fontsize': 12})
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
ax.axis('equal')
plt.tight_layout()

fig5, ax = plt.subplots()
ax.plot(rating_date['Date'], rating_date['Rating'])
plt.xticks(rotation=45, ha='right')

# ------- Build the layout -------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('**Evolution of total sales**')
    st.pyplot(fig1)

    st.text('')
    st.text('')
    st.markdown('**Evolution of rating**')
    st.pyplot(fig5)

with col2:
    st.markdown('**Quantity saled by product line**')
    st.pyplot(fig2)

    st.markdown('**Total sales by product line**')
    st.pyplot(fig3)

with col3:
    st.markdown('**Means of payment**')
    st.pyplot(fig4)

    st.text('')
    st.text('')
    st.text('')
    st.markdown("**KPI's per customer**")
    show_result_mgs(
            average_rating,
            average_unit_price,
            average_quantity_bought,
            average_total,
            average_gross_income
            )
