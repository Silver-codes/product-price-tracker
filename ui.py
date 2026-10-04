import requests
import streamlit as st

response = requests.get("http://127.0.0.1:8000/products")
response = requests.post("http://127.0.0.1:8000/products", json=product_to_add)
response = requests.delete(f"http://127.0.0.1:8000/tasks/{product_id}")
response = requests.get(f"http://127.0.0.1:8000/products/{product_id}/history")