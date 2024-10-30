import streamlit as st
import pandas as pd

# Load data
def load_data():
    df = pd.read_csv(r"C:\Users\HP\Documents\project\products_2.csv")
    
    # Ensure the necessary columns exist
    required_columns = ['Product Name', 'Category', 'Price (Naira)', 'Description']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Error: '{col}' column not found in the dataset.")
            return None

    # Return the DataFrame, dropping any rows with NA in required columns
    return df.dropna(subset=required_columns)

# Load the product data
df = load_data()

st.title("Ini's Online Store")

query = st.text_input("What would you like to purchase?", "")

if st.button("Search"):
    if query and df is not None:
        # Filter the DataFrame based on the search query
        results = df[df['Product Name'].str.contains(query, case=False)]

        if not results.empty:
            for _, row in results.iterrows():
                st.write(f"**Product Name:** {row['Product Name']}")
                st.write(f"**Category:** {row['Category']}")
                st.write(f"**Price:** {row['Price (Name)']}")
                if 'Description' in row and pd.notna(row['Description']):
                    st.write(f"**Description:** {row['Description']}")
                st.write("---")  # Separator for clarity
        else:
            st.write("No items found.")
    else:
        st.write("Please enter an item.")


