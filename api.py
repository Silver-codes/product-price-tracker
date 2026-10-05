import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select
from database import Product, ProductCreate, PriceHistory, init_db, engine
from scraper import fetch_product_price
from apscheduler.schedulers.background import BackgroundScheduler


# Periodically check product prices
def auto_update_prices():
    with Session(engine) as session:
        # 1. Fetch all items from the database
        products = session.exec(select(Product)).all()
        
        # 2. Loop through each item and perform the check
        for product in products:
            try:
                latest_price = fetch_product_price(product.product_url)
                # Create and save a new history entry
                log = PriceHistory(product_id=product.id, price=latest_price)
                session.add(log)
            except Exception as e:
                print(f"Error checking {product.id} {product.product_name}: {e}")                
        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Initialize and start the scheduler
    scheduler = BackgroundScheduler()
    # Run job every 15 minutes
    scheduler.add_job(auto_update_prices, "interval", minutes=15)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


# 1. Create product (uses ProductCreate input schema)
@app.post("/products", response_model=Product)
def create_product(product: ProductCreate):
    with Session(engine) as session:
        db_product = Product.model_validate(product)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product


# 2. Read all products (returns list of Product table items)
@app.get("/products", response_model=list[Product])
def read_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products


# 3. Delete product by database ID
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    with Session(engine) as session:
        product_to_delete = session.get(Product, product_id)
        if not product_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        session.delete(product_to_delete)
        session.commit()
        return {"message": f"Product with ID {product_id} deleted successfully"}


# 4. Scrape price & append to history by database ID
@app.post("/products/{product_id}/check")
async def update_price(product_id: int):
    with Session(engine) as session:
        product_to_update = session.get(Product, product_id)
        if not product_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        
        try:
            current_price = await asyncio.to_thread(fetch_product_price, product_to_update.product_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to scrape product price: {repr(e)}"
            )

        new_log = PriceHistory(product_id=product_to_update.id, price=current_price)
        session.add(new_log)
        session.commit()
        session.refresh(new_log)
        return new_log


# 5. Fetch all historical prices for a product
@app.get("/products/{product_id}/history", response_model=list[PriceHistory])
def get_product_prices(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
        statement = select(PriceHistory).where(PriceHistory.product_id == product_id)
        prices = session.exec(statement).all()
        return prices


#6. Update a product
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate):
    with Session(engine) as session:
        product_to_update = session.get(Product, product_id)
        if not product_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
        product_to_update.product_name = product.product_name
        product_to_update.product_url = product.product_url
        session.add(product_to_update)
        session.commit()
        session.refresh(product_to_update)
        return product_to_update





