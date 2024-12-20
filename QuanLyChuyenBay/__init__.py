import cloudinary as cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import quote
import oauthlib
from oauthlib.common import CLIENT_ID_CHARACTER_SET

# from flask_babelex import Babel


app = Flask(__name__, template_folder='template')
app.secret_key = "!@#$%^&*()"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/maybaydb?charset=utf8mb4' % quote('lam27072004Aa')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['CART_KEY'] = 'cart'

cloudinary.config(cloud_name='dtkzgdef1',
                  api_key='159519239888648',
                  api_secret='DZWRFYAgl22pGGAqsQhxjo-0H30')

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

gio_mua_toi_da = 12
gio_ban_toi_da = 4
thoi_gian_bay_toi_thieu = 1
san_bay_trung_gian_toi_da = 5
thoi_gian_dung_toi_da = 2
thoi_gian_dung_toi_thieu = 0.1

# Các thông số cần thiết từ tài khoản VNPay Sandbox
vnpay_config = {
    'vnp_TmnCode': 'PMAKVMOW',
    'vnp_HashSecret': 'USYEHCIUSVVCFQYKBQBZSUASXUXRSTCS',
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
}

# babel = Babel(app=app)
# @babel.localeselector
# def load_locale():
#     return 'vi'
