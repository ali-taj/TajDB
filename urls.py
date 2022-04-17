from views.api import *
from views.account import *
from views.products import Product

valid_urls = {
    "customers": Customers,
    "database_list": DataBase,
    "users": User,
    "dk_products": DKProducts,
    "products": Product,
}
