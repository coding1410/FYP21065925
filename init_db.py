from app import db
from models import Product

def init_db():
    db.drop_all()
    db.create_all()

    # Sample products
    products = [
        Product(name='Colorful Dog Collar', price=15.99, image='static/images/dog_collar.jpg', category='Accessories'),
        Product(name='Plush Dog Toy', price=9.99, image='static/images/dog_toy.jpg', category='Toys'),
        Product(name='Premium Dog Food', price=22.50, image='static/images/dog_food.jpg', category='Food'),
        Product(name='Dog Shampoo', price=8.45, image='static/images/dog_shampoo.jpg', category='Grooming')
    ]

    # Adding to session and committing to database
    db.session.bulk_save_objects(products)
    db.session.commit()

if __name__ == "__main__":
    init_db()
