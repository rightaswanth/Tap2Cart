

from requests import Session
from app.models.product import Category, Product, Subcategory


async def seed_product_data(db: Session):
    # --- Categories ---
    electronics = Category(category_name="Electronics", description="Electronic gadgets and devices.")
    groceries = Category(category_name="Groceries", description="Daily groceries and food items.")
    clothing = Category(category_name="Clothing", description="Men, women and kids clothing.")
    books = Category(category_name="Books", description="Educational and entertainment books.")
    home_appliances = Category(category_name="Home Appliances", description="Appliances for daily home use.")
    db.add_all([electronics, groceries, clothing, books, home_appliances])
    await db.commit()

    # --- Subcategories ---
    # Electronics
    laptops = Subcategory(subcategory_name="Laptops", category_id=electronics.category_id)
    mobiles = Subcategory(subcategory_name="Mobiles", category_id=electronics.category_id)
    accessories = Subcategory(subcategory_name="Accessories", category_id=electronics.category_id)

    # Groceries
    fruits = Subcategory(subcategory_name="Fruits", category_id=groceries.category_id)
    vegetables = Subcategory(subcategory_name="Vegetables", category_id=groceries.category_id)
    beverages = Subcategory(subcategory_name="Beverages", category_id=groceries.category_id)

    # Clothing
    mens = Subcategory(subcategory_name="Men's Wear", category_id=clothing.category_id)
    womens = Subcategory(subcategory_name="Women's Wear", category_id=clothing.category_id)
    kids = Subcategory(subcategory_name="Kids' Wear", category_id=clothing.category_id)

    # Books
    fiction = Subcategory(subcategory_name="Fiction", category_id=books.category_id)
    education = Subcategory(subcategory_name="Education", category_id=books.category_id)
    comics = Subcategory(subcategory_name="Comics", category_id=books.category_id)

    # Home Appliances
    kitchen = Subcategory(subcategory_name="Kitchen", category_id=home_appliances.category_id)
    cleaning = Subcategory(subcategory_name="Cleaning", category_id=home_appliances.category_id)
    comfort = Subcategory(subcategory_name="Comfort", category_id=home_appliances.category_id)

    db.add_all([
        laptops, mobiles, accessories,
        fruits, vegetables, beverages,
        mens, womens, kids,
        fiction, education, comics,
        kitchen, cleaning, comfort
    ])
    await db.commit()

    # --- Products (at least 30) ---
    products = [
        # Electronics
        Product(product_name="MacBook Pro", price=2000.00, description="Apple laptop.", stock_quantity=10,
                category_id=electronics.category_id, subcategory_id=laptops.subcategory_id),
        Product(product_name="Dell XPS", price=1500.00, description="High-performance laptop.", stock_quantity=12,
                category_id=electronics.category_id, subcategory_id=laptops.subcategory_id),
        Product(product_name="iPhone 14", price=999.00, description="Latest Apple smartphone.", stock_quantity=20,
                category_id=electronics.category_id, subcategory_id=mobiles.subcategory_id),
        Product(product_name="Samsung Galaxy S23", price=850.00, description="Flagship Android smartphone.", stock_quantity=18,
                category_id=electronics.category_id, subcategory_id=mobiles.subcategory_id),
        Product(product_name="Wireless Mouse", price=25.00, description="Ergonomic mouse.", stock_quantity=100,
                category_id=electronics.category_id, subcategory_id=accessories.subcategory_id),
        Product(product_name="Mechanical Keyboard", price=120.00, description="RGB gaming keyboard.", stock_quantity=50,
                category_id=electronics.category_id, subcategory_id=accessories.subcategory_id),

        # Groceries
        Product(product_name="Bananas", price=1.20, description="Fresh bananas.", stock_quantity=150,
                category_id=groceries.category_id, subcategory_id=fruits.subcategory_id),
        Product(product_name="Tomatoes", price=2.00, description="Organic tomatoes.", stock_quantity=200,
                category_id=groceries.category_id, subcategory_id=vegetables.subcategory_id),
        Product(product_name="Coca Cola 2L", price=3.00, description="Refreshing drink.", stock_quantity=80,
                category_id=groceries.category_id, subcategory_id=beverages.subcategory_id),
        Product(product_name="Mangoes", price=2.50, description="Sweet mangoes.", stock_quantity=120,
                category_id=groceries.category_id, subcategory_id=fruits.subcategory_id),
        Product(product_name="Potatoes", price=1.00, description="Fresh potatoes.", stock_quantity=300,
                category_id=groceries.category_id, subcategory_id=vegetables.subcategory_id),
        Product(product_name="Pepsi 1.5L", price=2.50, description="Soft drink.", stock_quantity=60,
                category_id=groceries.category_id, subcategory_id=beverages.subcategory_id),

        # Clothing
        Product(product_name="Men's T-Shirt", price=20.00, description="Cotton t-shirt.", stock_quantity=70,
                category_id=clothing.category_id, subcategory_id=mens.subcategory_id),
        Product(product_name="Men's Jeans", price=40.00, description="Denim jeans.", stock_quantity=50,
                category_id=clothing.category_id, subcategory_id=mens.subcategory_id),
        Product(product_name="Women's Dress", price=60.00, description="Casual dress.", stock_quantity=40,
                category_id=clothing.category_id, subcategory_id=womens.subcategory_id),
        Product(product_name="Women's Jacket", price=80.00, description="Winter jacket.", stock_quantity=25,
                category_id=clothing.category_id, subcategory_id=womens.subcategory_id),
        Product(product_name="Kids' Hoodie", price=25.00, description="Hoodie for kids.", stock_quantity=60,
                category_id=clothing.category_id, subcategory_id=kids.subcategory_id),
        Product(product_name="Kids' Shorts", price=15.00, description="Summer shorts.", stock_quantity=100,
                category_id=clothing.category_id, subcategory_id=kids.subcategory_id),

        # Books
        Product(product_name="Harry Potter", price=15.00, description="Fantasy novel.", stock_quantity=80,
                category_id=books.category_id, subcategory_id=fiction.subcategory_id),
        Product(product_name="Lord of the Rings", price=18.00, description="Epic fantasy book.", stock_quantity=60,
                category_id=books.category_id, subcategory_id=fiction.subcategory_id),
        Product(product_name="Python Programming", price=45.00, description="Learn Python coding.", stock_quantity=30,
                category_id=books.category_id, subcategory_id=education.subcategory_id),
        Product(product_name="Data Science Handbook", price=55.00, description="Guide for data science.", stock_quantity=25,
                category_id=books.category_id, subcategory_id=education.subcategory_id),
        Product(product_name="Marvel Comics Vol.1", price=12.00, description="Superhero comics.", stock_quantity=100,
                category_id=books.category_id, subcategory_id=comics.subcategory_id),
        Product(product_name="DC Comics Vol.1", price=12.00, description="Batman & Superman comics.", stock_quantity=100,
                category_id=books.category_id, subcategory_id=comics.subcategory_id),

        # Home Appliances
        Product(product_name="Microwave Oven", price=200.00, description="20L microwave oven.", stock_quantity=15,
                category_id=home_appliances.category_id, subcategory_id=kitchen.subcategory_id),
        Product(product_name="Blender", price=80.00, description="Kitchen blender.", stock_quantity=30,
                category_id=home_appliances.category_id, subcategory_id=kitchen.subcategory_id),
        Product(product_name="Vacuum Cleaner", price=150.00, description="Bagless vacuum cleaner.", stock_quantity=20,
                category_id=home_appliances.category_id, subcategory_id=cleaning.subcategory_id),
        Product(product_name="Air Conditioner", price=1200.00, description="1.5 ton split AC.", stock_quantity=10,
                category_id=home_appliances.category_id, subcategory_id=comfort.subcategory_id),
        Product(product_name="Ceiling Fan", price=60.00, description="Energy efficient fan.", stock_quantity=40,
                category_id=home_appliances.category_id, subcategory_id=comfort.subcategory_id),
        Product(product_name="Dishwasher", price=800.00, description="Automatic dishwasher.", stock_quantity=8,
                category_id=home_appliances.category_id, subcategory_id=kitchen.subcategory_id),
    ]

    db.add_all(products)
    await db.commit()

    return {"message": "Database seeded with categories, subcategories, and 30+ products!"}
