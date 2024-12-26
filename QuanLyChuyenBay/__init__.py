import cloudinary as cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import quote
import oauthlib
from oauthlib.common import CLIENT_ID_CHARACTER_SET

# from flask_babelex import Babel


app = Flask(__name__, template_folder='template')
app.secret_key = "!@#$%^&*dasdafaádasds()"
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
thoi_gian_dung_toi_da = 30
thoi_gian_dung_toi_thieu = 20

VN_PAY_CONFIG = {
    'vnp_TmnCode': 'PMAKVMOW',
    'vnp_HashSecret': 'USYEHCIUSVVCFQYKBQBZSUASXUXRSTCS',
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
}

MOMO_CONFIG = {
    'partner_code': 'MOMO',
    'access_key': 'YOUR_ACCESS_KEY',
    'secret_key': 'YOUR_SECRET_KEY',
    'endpoint': 'https://test-payment.momo.vn/gw_payment/transactionProcessor',
    'return_url': 'http://127.0.0.1:5000/momo_return',
    'notify_url': 'http://127.0.0.1:5000/momo_notify'
}


# babel = Babel(app=app)
# @babel.localeselector
# def load_locale():
#     return 'vi'


SAN_BAY_TONG_SO = 10
THOI_GIAN_BAY_TOI_THIEU = 30  # phút
SAN_BAY_TRUNG_GIAN_TOI_DA = 2
THOI_GIAN_DUNG_TOI_THIEU = 20  # phút
THOI_GIAN_DUNG_TOI_DA = 30  # phút
GIO_BAN_VE_TOI_DA_TRUOC_KH_KHOI_HANH = 4  # giờ


class QuyDinh(db.Model):
    __tablename__ = 'quy_dinh'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    so_luong_san_bay_max = db.Column(db.Integer, nullable=False)
    thoi_gian_bay_toi_thieu = db.Column(db.Integer, nullable=False)  # Thời gian bay tối thiểu tính bằng phút
    so_san_bay_trung_gian_max = db.Column(db.Integer, nullable=False)
    thoi_gian_dung_min = db.Column(db.Integer, nullable=False)  # Thời gian dừng tối thiểu tại sân bay trung gian
    thoi_gian_dung_max = db.Column(db.Integer, nullable=False)  # Thời gian dừng tối đa tại sân bay trung gian
    so_luong_hang_ve = db.Column(db.Integer, nullable=False)  # Số lượng hạng vé
    thoi_gian_ban_ve = db.Column(db.Integer, nullable=False)  # Thời gian bán vé (ví dụ: 48 giờ trước chuyến bay)
    thoi_gian_dat_ve = db.Column(db.Integer,
                                 nullable=False)  # Thời gian đặt vé trước chuyến bay (ví dụ: 30 phút trước chuyến bay)
    don_gia_ve = db.Column(db.Float, nullable=False)  # Đơn giá vé mặc định



class QuyDinh:
    def __init__(self):
        self.gio_ban_toi_da = 4  # Giờ trước chuyến bay, không bán vé nếu ít hơn 4 giờ
        self.thoi_gian_bay_toi_thieu = 30  # Phút, thời gian bay tối thiểu
        self.so_san_bay_trung_gian_toi_da = 2  # Số sân bay trung gian tối đa
        self.thoi_gian_dung_min = 20  # Phút, thời gian dừng tối thiểu tại sân bay trung gian
        self.thoi_gian_dung_max = 30  # Phút, thời gian dừng tối đa tại sân bay trung gian
        self.so_ghe_hang_1 = 100  # Số lượng ghế hạng 1
        self.so_ghe_hang_2 = 150  # Số lượng ghế hạng 2

