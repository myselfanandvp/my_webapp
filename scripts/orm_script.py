from users.models import User
from products.models import Product,Category,ProductImage,Brand,ProductReview,ProductOffers,CategoryOffer
from users.models import AddressModel,User
from profiles.models import Wallet
from pprint import pprint
from django.db import connection
from datetime import datetime
from time import sleep
from django.db.models import Q,F
from wishlist.models import WishList
from cart.models import Cart
from checkout.models import Order , OrderItem
from django.db.models import Avg,Max
from adminpanel.models import Coupon , CouponUsage
import string
import secrets


# brands = [
#     Brand(name="Apple", slug="apple"),
#     Brand(name="Samsung", slug="samsung"),
#     Brand(name="Google", slug="google"),
#     Brand(name="Fitbit", slug="fitbit"),
#     Brand(name="Garmin", slug="garmin"),
#     Brand(name="Amazfit", slug="amazfit"),
#     Brand(name="OnePlus", slug="oneplus"),
#     Brand(name="boAt", slug="boat"),
#     Brand(name="Fastrack", slug="fastrack"),
#     Brand(name="Lava", slug="lava"),
#     Brand(name="Sony", slug="sony"),
#     Brand(name="Bose", slug="bose"),
#     Brand(name="Sennheiser", slug="sennheiser"),
#     Brand(name="JBL", slug="jbl"),
#     Brand(name="Beats", slug="beats"),
#     Brand(name="Skullcandy", slug="skullcandy"),
#     Brand(name="Anker", slug="anker"),
#     Brand(name="Shure", slug="shure"),
#     Brand(name="Marshall", slug="marshall"),
#     Brand(name="Philips", slug="philips"),
#     Brand(name="Realme", slug="realme"),
#     Brand(name="Noise", slug="noise"),
#     Brand(name="Boult Audio", slug="boult-audio"),
#     Brand(name="Fire-Boltt", slug="fire-boltt"),
#     Brand(name="Huawei", slug="huawei"),
#     Brand(name="Xiaomi", slug="xiaomi"),
#     Brand(name="Nothing", slug="nothing"),
# ]


# Brand.objects.bulk_create(brands)

# categories = [
#     # Smartwatch Categories
#     Category(name="Fitness", slug="fitness", type="smartwatch"),
#     Category(name="Health Monitoring", slug="health-monitoring", type="smartwatch"),
#     Category(name="Lifestyle", slug="lifestyle", type="smartwatch"),
#     Category(name="Sports", slug="sports", type="smartwatch"),
#     Category(name="Outdoor", slug="outdoor", type="smartwatch"),
#     Category(name="Luxury", slug="luxury", type="smartwatch"),
#     Category(name="Kids", slug="kids", type="smartwatch"),
#     Category(name="Hybrid", slug="hybrid", type="smartwatch"),
#     Category(name="Budget", slug="budget", type="smartwatch"),
#     Category(name="Premium", slug="premium", type="smartwatch"),
#     Category(name="Android Compatible", slug="android-compatible", type="smartwatch"),
#     Category(name="iOS Compatible", slug="ios-compatible", type="smartwatch"),
#     Category(name="Calling Smartwatch", slug="calling-smartwatch", type="smartwatch"),
#     Category(name="Rugged", slug="rugged", type="smartwatch"),
#     Category(name="New Arrival",slug='new-arrival',type="new_arrival"),

#     # Headphone Categories (excluding duplicate names)
#     Category(name="Over-Ear", slug="over-ear", type="headphone"),

#     Category(name="On-Ear", slug="on-ear", type="headphone"),
#     Category(name="In-Ear", slug="in-ear", type="headphone"),
#     Category(name="True Wireless Earbuds (TWS)", slug="tws", type="headphone"),
#     Category(name="Wired", slug="wired", type="headphone"),
#     Category(name="Wireless", slug="wireless", type="headphone"),
#     Category(name="Noise Cancelling", slug="noise-cancelling", type="headphone"),
#     Category(name="Gaming", slug="gaming", type="headphone"),
#     Category(name="Studio Monitoring", slug="studio-monitoring", type="headphone"),
#     Category(name="Bone Conduction", slug="bone-conduction", type="headphone"),
#     Category(name="Neckband", slug="neckband", type="headphone"),
#     Category(name="DJ", slug="dj", type="headphone"),
# ]

# Category.objects.bulk_create(categories)




pprint(connection.queries)