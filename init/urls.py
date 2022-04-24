from views.api import *
from views.account import *
from views.file import FileManager
from views.products import Product
from views.site_config import Main, Category

valid_urls = {
    "database_list": DataBase,
    "main": Main,
    "category": Category,
    "file_manager": FileManager,
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
