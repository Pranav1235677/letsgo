import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Function to generate a simulated dataset
def generate_data(month):
    categories = [
        "Food", "Transportation", "Bills", "Groceries", "Entertainment", 
        "Healthcare", "Shopping", "Dining", "Travel", "Education",
        "Electricity", "Household Items", "Festive Expenses"
    ]  # Added "Electricity", "Household Items", and "Festive Expenses"
    
    payment_modes = ["Cash", "Online", "NetBanking", "Credit Card", "Debit Card", "Wallet"]
    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    data = []
    for _ in range(51):
        random_date = fake.date_between_dates(
            date_start=pd.Timestamp(year=2024, month=month_mapping[month], day=1),
            date_end=pd.Timestamp(year=2024, month=month_mapping[month], day=28)
        )
        data.append({
            "Date": random_date,
            "Category": random.choice(categories),
            "Payment_Mode": random.choice(payment_modes),
            "Description": random.choice([
                "Bought vegetables",
                "Paid electricity bill",
                "School fees payment",
                "Gas cylinder refill",
                "Groceries for home",
                "Milk and dairy items",
                "Medicine purchase",
                "Mobile recharge",
                "Monthly rent",
                "Dining at a restaurant",
                "Purchase of stationery",
                "House cleaning items",
                "Temple donation",
                "Shopping at local market",
                "Water bill payment",
                "Internet recharge",
                "Cable TV subscription",
                "New clothes purchase",
                "Repair work at home",
                "Train ticket booking",
                "Bus pass renewal",
                "Housemaid salary",
                "Fruit purchase",
                "Doctor consultation fee",
                "Car petrol refill",
                "Bike service expense",
                "Festival decorations",
                "Gift for a family member",
                "Newspaper subscription"
            ]),
            "Amount_Paid": round(random.uniform(10.0, 500.0), 2),
            "Cashback": round(random.uniform(0.0, 20.0), 2),
            "Month": month
        })
    return pd.DataFrame(data)

# Function to initialize the SQLite database with month-specific tables
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    for month in months:
        table_name = month.lower()  # Use lowercase for table names
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                Date TEXT,
                Category TEXT,
                Payment_Mode TEXT,
                Description TEXT,
                Amount_Paid REAL,
                Cashback REAL,
                Month TEXT
            )
        """)
    conn.commit()
    conn.close()

# Function to load data into the appropriate month table
def load_data_to_db(data, month):
    conn = sqlite3.connect('expenses.db')
    table_name = month.lower()
    data.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

# Function to query data from a specific or all tables
def query_data_from_table(table=None):
    conn = sqlite3.connect('expenses.db')
    if table:  # Query a specific table
        result = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY Date ASC", conn)
    else:  # Query data from all month tables
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        dataframes = []
        for month in months:
            table_name = month.lower()
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            dataframes.append(df)
        result = pd.concat(dataframes, ignore_index=True)
    conn.close()
    return result

# Initialize the database
init_db()

# Apply custom CSS for styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #eaf4fc;
        }
        h1, h2, h3 {
            color: #6c63ff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_custom_css()

# Main Streamlit app
st.title("Personal Expense Tracker")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose an option",
    ["Generate Data", "View Data", "Visualize Insights", "Run SQL Query", "Run Predefined SQL Queries"]
)

if option == "Generate Data":
    st.subheader("Generate Expense Data")
    month = st.text_input("Enter the month (e.g., January):", "January")
    if st.button("Generate"):
        try:
            data = generate_data(month)
            load_data_to_db(data, month)
            st.success(f"Data for {month} generated and loaded into the database!")
            st.dataframe(data.head())
        except KeyError:
            st.error("Invalid month entered. Please ensure the month is spelled correctly.")

elif option == "View Data":
    st.subheader("View Expense Data")
    selection = st.selectbox("Choose data scope", ["Specific Month", "All Months"])
    if selection == "Specific Month":
        month = st.text_input("Enter the month to view data (e.g., January):", "January")
        if st.button("View"):
            try:
                table = month.lower()
                data = query_data_from_table(table)
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("View All"):
            try:
                data = query_data_from_table()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Visualize Insights":
    st.subheader("Spending Insights")
    selection = st.selectbox("Choose data scope", ["Specific Month", "All Months"])
    if selection == "Specific Month":
        month = st.text_input("Enter the month to visualize data (e.g., January):", "January")
        if st.button("Visualize"):
            try:
                table = month.lower()
                data = query_data_from_table(table)
                if not data.empty:
                    category_spending = data.groupby("Category")["Amount_Paid"].sum()
                    st.bar_chart(category_spending)

                    fig, ax = plt.subplots()
                    ax.pie(category_spending, labels=category_spending.index, autopct='%1.1f%%', startangle=140)
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("Visualize All"):
            try:
                data = query_data_from_table()
                if not data.empty:
                    category_spending = data.groupby("Category")["Amount_Paid"].sum()
                    st.bar_chart(category_spending)

                    fig, ax = plt.subplots()
                    ax.pie(category_spending, labels=category_spending.index, autopct='%1.1f%%', startangle=140)
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"An error occurred: {e}")
