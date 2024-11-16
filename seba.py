import streamlit as st
import pandas as pd
import sqlite3
from fuzzywuzzy import process

# Initialize database
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Create cart table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()
    conn.close()

# Initialize database
init_db()

# User Registration
def register_user(username, password, role="Buyer"):
    try:
        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# User Authentication
def authenticate_user(username, password):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user if user else None

# Cart Management
def add_to_cart_db(user_id, product_name, price):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, quantity FROM cart WHERE user_id = ? AND product_name = ?", (user_id, product_name))
    item = cursor.fetchone()
    if item:
        cursor.execute("UPDATE cart SET quantity = ? WHERE id = ?", (item[1] + 1, item[0]))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_name, price, quantity) VALUES (?, ?, ?, 1)",
                       (user_id, product_name, price))
    conn.commit()
    conn.close()

def get_cart_items(user_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, price, quantity FROM cart WHERE user_id = ?", (user_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def remove_from_cart(user_id, product_name):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_name = ?", (user_id, product_name))
    conn.commit()
    conn.close()

# Load product data
def load_data():
    try:
        df = pd.read_csv(r"C:\Users\HP\Documents\project\products_2.csv")
    except FileNotFoundError:
        st.error("Error: The products file could not be found.")
        return None

    required_columns = ['Product Name', 'Category', 'Price (Naira)', 'Description']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Error: '{col}' column not found in the dataset.")
            return None

    return df.dropna(subset=required_columns)

# Save updated data to CSV
def save_data(df):
    df.to_csv(r"C:\Users\HP\Documents\project\products_2.csv", index=False)
    st.success("Product list updated successfully!")

# Login
def user_login():
    st.title("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    create_account = st.checkbox("Create new account")
    role = st.selectbox("Role", ["Buyer", "Seller"]) if create_account else None

    if st.button("Login"):
        if create_account:
            if register_user(username, password, role):
                st.success(f"Account created successfully as {role}! You can now log in.")
            else:
                st.error("Username already exists. Please choose another username.")
        else:
            user = authenticate_user(username, password)
            if user:
                st.session_state.current_user = {"id": user[0], "username": username, "role": user[1]}
                st.success(f"Login successful as {user[1]}!")
            else:
                st.error("Incorrect username or password.")

# Logout function
def logout():
    st.session_state.current_user = None
    st.session_state.users = {}  # Clear users data to reset everything
    st.success("You have logged out successfully.")


#Cart Preview
def show_cart_preview():
    if not st.session_state.current_user or st.session_state.current_user["role"] != "Buyer":
        return

    user_id = st.session_state.current_user["id"]
    cart_items = get_cart_items(user_id)

    st.sidebar.write(f"**Cart ({len(cart_items)} items)**" if cart_items else "Your cart is empty.")

    for product_name, price, quantity in cart_items:
        st.sidebar.write(f"{product_name} - {quantity} x {price} Naira")

        # Allow the user to adjust the quantity
        new_quantity = st.sidebar.number_input(
            f"Quantity for {product_name}",
            min_value=1,
            max_value=100,
            value=quantity,
            key=f"{product_name}_qty"
        )

        # Only update the database if the quantity changes
        if new_quantity != quantity:
            if st.sidebar.button(f"Update {product_name} Quantity", key=f"update_{product_name}"):
                update_cart_quantity(user_id, product_name, new_quantity)
                st.success(f"Updated {product_name} quantity to {new_quantity}!")
                #st.experimental_rerun()

        # Button to remove the item from the cart
        if st.sidebar.button(f"Remove {product_name}", key=f"remove_{product_name}"):
            remove_from_cart(user_id, product_name)
            #st.experimental_rerun()


# Helper function to update the cart quantity
def update_cart_quantity(user_id, product_name, new_quantity):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_name = ?",
        (new_quantity, user_id, product_name)
    )
    conn.commit()
    conn.close()



# Add this helper function to update the cart quantity
def update_cart_quantity(user_id, product_name, new_quantity):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_name = ?",
        (new_quantity, user_id, product_name)
    )
    conn.commit()
    conn.close()

# Buyer Interface
def buyer_interface(df):
    if 'current_user' in st.session_state and st.session_state.current_user is not None:
        username = st.session_state.current_user.get('username')  
        st.header(f"Welcome to Ini's Online Store, {st.session_state.current_user['username']}!")
    else:
        st.header(f"Welcome to Ini's Online Store,Buyer")
    categories = df['Category'].unique().tolist()
    categories.insert(0, 'All Categories')  # Add 'All Categories' option at the top
    selected_category = st.selectbox("Select Category (Optional)", categories)

    # Standardize the category comparison (lowercase and strip)
    df['Category'] = df['Category'].str.strip().str.lower()

    if selected_category != 'All Categories':
        selected_category = selected_category.strip().lower()  # Standardize the selected category

        # Check if the category exists in the product list
        if selected_category not in df['Category'].unique():
            st.warning(f"Category '{selected_category}' not found in the product list.")
        else:
            matched_products = df[df['Category'] == selected_category]
    else:
        matched_products = df

    # Search bar for product name
    query = st.text_input("What would you like to purchase?", "")
    if query:
        matches = process.extract(query, matched_products['Product Name'].tolist(), limit=15)
        matched_products = matched_products[matched_products['Product Name'].isin([match[0] for match in matches])]

    for _, row in matched_products.iterrows():
        st.write(f"**{row['Product Name']}** - {row['Price (Naira)']} Naira")
        st.write(row['Description'])
        button_key = f"add_to_cart_{row['Product Name']}_{_}"

        if st.button(f"Add {row['Product Name']} to Cart", key=button_key):
            if st.session_state.current_user is None:
                st.warning("Please log in to add items to your cart!")
            else:
                user_id = st.session_state.current_user["id"]
                add_to_cart_db(user_id, row['Product Name'], row['Price (Naira)'])
                st.success(f"{row['Product Name']} added to your cart!")


# Seller Interface
def seller_interface(df):
    st.header("Seller Interface")
    action = st.selectbox("Choose an action:", ["Add Product", "Update Product", "Delete Product"])

    if action == "Add Product":
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        price = st.number_input("Price (Naira)", min_value=1)
        description = st.text_area("Description")
        if st.button("Add Product"):
            new_product = pd.DataFrame({
                'Product Name': [name],
                'Category': [category],
                'Price (Naira)': [price],
                'Description': [description]
            })
            df = pd.concat([df, new_product], ignore_index=True)
            save_data(df)

    elif action == "Update Product":
        product_names = df['Product Name'].tolist()
        product_to_update = st.selectbox("Select product to update", product_names)
        updated_price = st.number_input("New Price (Naira)", min_value=1)
        updated_description = st.text_area("New Description")
        if st.button("Update Product"):
            df.loc[df['Product Name'] == product_to_update, ['Price (Naira)', 'Description']] = [updated_price, updated_description]
            save_data(df)

    elif action == "Delete Product":
        product_names = df['Product Name'].tolist()
        product_to_delete = st.selectbox("Select product to delete", product_names)
        if st.button("Delete Product"):
            df = df[df['Product Name'] != product_to_delete]
            save_data(df)


import time


# Main function to run the app
def main():
    st.sidebar.image(r"C:\Users\HP\AppData\Local\Temp\e7575cc4-116c-4dd1-b4c7-3fa60af93482_Black and White Elegant Fashion Brand Logo.zip.482\1.png", use_column_width=True)
    # First, check if the user is logged in (this will only be true if the user is logged in)
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None  # Ensure session_state is initialized
    # I
    #If user is not logged in, show login form
    if st.session_state.current_user is None:
        st.title("Login to Ini's Online Store")
        user_login()  # Show the login form
        return  # Stop here and don't show the rest of the page content
    
             
    # If logged in, display role-based content
    else:
        # Role-based content after login
        role = st.session_state.current_user["role"]
        df = load_data()  # Load product data (replace with your actual function)
            # Logout button
        if st.sidebar.button("Logout"):
            logout()        
        if role == "Buyer":
            # Show buyer interface
            show_cart_preview()
            buyer_interface(df)


        elif role == "Seller":
            # Show seller interface
            seller_interface(df)

if __name__ == "__main__":
    main()






