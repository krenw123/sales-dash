
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load the Excel file
data = pd.read_excel("exampledata2.xlsx", engine="openpyxl")

# Rename columns for consistency
data = data.rename(columns={"Invoice date": "Date", "Product": "SKU", "Quantity": "Sales"})

# Convert date column to datetime
data["Date"] = pd.to_datetime(data["Date"])

# Extract year and month
data["YearMonth"] = data["Date"].dt.to_period("M")

# Aggregate monthly sales per SKU
monthly_sales = data.groupby(["SKU", "YearMonth"])["Sales"].sum().reset_index()

# Pivot for easier charting
pivot_table = monthly_sales.pivot(index="YearMonth", columns="SKU", values="Sales").fillna(0)

# Streamlit app
st.title("Sales Dashboard")

# Product selector
selected_skus = st.multiselect("Select SKUs to view", options=monthly_sales["SKU"].unique(), default=monthly_sales["SKU"].unique()[:5])

# Plot monthly sales trends
st.subheader("Monthly Sales Trends")
for sku in selected_skus:
    sku_data = monthly_sales[monthly_sales["SKU"] == sku]
   

fig, ax = plt.subplots()
ax.bar(sku_data["YearMonth"].astype(str), sku_data["Sales"], color='skyblue')
ax.set_title(f"Monthly Sales for {sku}")
ax.set_xlabel("Month")
ax.set_ylabel("Sales")
ax.set_ylim(bottom=0)
plt.xticks(rotation=45)
st.pyplot(fig)



# Flag SKUs with July sales > 130% of Apr-Jun average
st.subheader("Flagged SKUs (July Sales > 130% of Apr–Jun Avg)")

# Filter for April to July
monthly_sales["Month"] = monthly_sales["YearMonth"].dt.month
monthly_sales["Year"] = monthly_sales["YearMonth"].dt.year
filtered = monthly_sales[(monthly_sales["Year"] == 2023) & (monthly_sales["Month"].isin([4, 5, 6, 7]))]

# Calculate April–June average and July sales
apr_jun = filtered[filtered["Month"].isin([4, 5, 6])].groupby("SKU")["Sales"].mean()
july = filtered[filtered["Month"] == 7].groupby("SKU")["Sales"].sum()

# Compare and flag
flagged = pd.DataFrame({
    "July Sales": july,
    "Apr–Jun Avg Sales": apr_jun
})
flagged = flagged.dropna()
flagged["% Increase"] = ((flagged["July Sales"] - flagged["Apr–Jun Avg Sales"]) / flagged["Apr–Jun Avg Sales"]) * 100
flagged = flagged[flagged["% Increase"] > 30].sort_values(by="% Increase", ascending=False)

st.dataframe(flagged)

# CSV export
def convert_df(df):
    return df.to_csv(index=True).encode('utf-8')

csv = convert_df(flagged)
st.download_button(
    label="Download flagged SKUs as CSV",
    data=csv,
    file_name='flagged_skus.csv',
    mime='text/csv',
)
