from views.api import *
from views.account import *
from views.products import Product

valid_urls = {
    "database_list": DataBase,
    # "main": Main,
    # "file_manager": FileManager,
    # "dashboard": Dashboard,
    # "comment": Comment,
    # "bookmark": Bookmark,
    # "ticket": Ticket,
    # "order": Order,
    # "address": Address,
    # "wallet": Wallet,
    # "affiliate": Affiliate,
    # "payment": Payment,
    "users": User,
    "products": Product,
    "dk_products": DKProducts,
}
