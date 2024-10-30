import streamlit as st
import pandas as pd
from fuzzywuzzy import process

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
        # Get a list of product names
        product_names = df['Product Name'].tolist()
        
        # Use fuzzy matching to find the best matches
        matches = process.extract(query, product_names)

        # Filter results based on the matches
        results = df[df['Product Name'].isin([match[0] for match in matches])]

        if not results.empty:
            for _, row in results.iterrows():
                st.write(f"**Product Name:** {row['Product Name']}")
                st.write(f"**Category:** {row['Category']}")
                st.write(f"**Price:** {row['Price (Naira)']}")
                if 'Description' in row and pd.notna(row['Description']):
                    st.write(f"**Description:** {row['Description']}")
                st.write("---")  # Separator for clarity
        else:
            st.write("No items found.")
    else:
        st.write("Please enter an item.")
