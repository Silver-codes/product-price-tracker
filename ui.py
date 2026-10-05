import requests
import streamlit as st
import pandas as pd

#API URL
fastapi_url = "http://127.0.0.1:8000"

##Function section
#fetch all products
def get_products():
    try:
        response = requests.get(f"{fastapi_url}/products")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server. Is FastAPI running?")
    return []

#Add a product
def add_product(name, url):
    try:
        response = requests.post(f"{fastapi_url}/products", json={"product_name": name, "product_url": url})
        if response.status_code == 200:
            st.write("Product added successfully!")
            return True
        else:
            st.error(f"Status code: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server. Is FastAPI running?")
        return False

#Fetch price history of a product
def get_price_history(product_id):
    try:
        response = requests.get(f"{fastapi_url}/products/{product_id}/history")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server. Is FastAPI running?")
    return []

#Delete a product
def delete_product(product_id):
    try:
        response = requests.delete(f"{fastapi_url}/products/{product_id}")
        if response.status_code == 200:
            st.write("Product deleted succesfully")
            return True
        else:
            st.error(f"Status code: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend server. Is FastAPI running?")
    return False



###UI section
all_products = get_products()
##Sidebar
#Add product UI
st.sidebar.header("Add new product to track")

with st.sidebar.form(key="add_product_form"):
    product_name = st.text_input("Product Name")
    product_url = st.text_input("Product URL")
    submit_button = st.form_submit_button(label="Add Product")
if submit_button:
    if product_name and product_url:
        success = add_product(product_name, product_url)
        if success:
            st.sidebar.success("Product added successfully!")
            st.rerun()
    else:
        st.sidebar.warning("Please fill out all field")

#Delete product
if all_products:
    st.sidebar.divider()
    st.sidebar.header("Delete tracked product")

    delete_options = {p["product_name"]: p["id"] for p in all_products}
    selected_delete_name = st.sidebar.selectbox("Select product to delete",
        list(delete_options.keys()),
        key="delete_selector"
    )

    if st.sidebar.button("Delete Product", type="primary"):
        product_to_remove_id = delete_options[selected_delete_name]
        if delete_product(product_to_remove_id):
            st.sidebar.success(f"Deleted '{selected_delete_name}'!")
            st.rerun()







##Main body
#Main Title
st.title("Product Price Tracker")
#Main dashboard view
st.header("Your products")
if all_products:
    df = pd.DataFrame(all_products)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No products to display yet. Add a product to get started!")

#Price history lookup
if all_products:
    product_options = {p["product_name"]: p["id"] for p in all_products}
    selected_name = st.selectbox("Select a product to view price history", list(product_options.keys()))
    selected_id = product_options[selected_name]
    if selected_id:
        history_data = get_price_history(selected_id)
        
        if history_data:
            df_history = pd.DataFrame(history_data)
            df_history["timestamp"] = pd.to_datetime(df_history["timestamp"])
            st.subheader(f"Price History for {selected_name}")
            st.line_chart(data=df_history, x="timestamp", y="price")
        else:
           st.info(f"No price history data available for {selected_name} yet.")






# response = requests.get("http://127.0.0.1:8000/products")
# response = requests.post("http://127.0.0.1:8000/products", json=product_to_add)
# response = requests.delete(f"http://127.0.0.1:8000/tasks/{product_id}")
# response = requests.get(f"http://127.0.0.1:8000/products/{product_id}/history")