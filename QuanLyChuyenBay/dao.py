import json
import math
import re
import urllib
import uuid

import requests
from flask import request
from flask_sqlalchemy.session import Session
from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy.sql.sqltypes import NULLTYPE

from QuanLyChuyenBay.models import MayBay, ChuyenBay, TuyenBay, SanBay, User, Ve, Role, KhachHang, SanBayTrungGian,GheMayBay
from QuanLyChuyenBay import db
import datetime
from flask_login import current_user
import hashlib
from sqlalchemy import func
from sqlalchemy.sql import extract
from datetime import datetime
import hmac
from sqlalchemy.exc import IntegrityError
import urllib.parse
import time


def load_san_bay():
    return SanBay.query.all()


def load_may_bay():
    return MayBay.query.all()


def load_tuyen_bay():
    return TuyenBay.query.all()

def load_san_bay():
    return SanBay.query.all()


def load_chuyen_bay(from_place, to_place, date):
    query = db.session.query(ChuyenBay).join(TuyenBay)

    # Lọc theo sân bay đi nếu có giá trị
    if from_place:
        query = query.filter(TuyenBay.san_bay_di.has(SanBay.ten_sb == from_place))

    # Lọc theo sân bay đến nếu có giá trị
    if to_place:
        query = query.filter(TuyenBay.san_bay_den.has(SanBay.ten_sb == to_place))

    # Lọc theo ngày bay nếu có giá trị
    if date:
        query = query.filter(ChuyenBay.ngay_gio_bay.like(f"{date}%"))

    return query.all()


def get_chuyen_bay_by_id(flight_id):
    return db.session.query(ChuyenBay).filter(ChuyenBay.id == flight_id).one_or_none()

def get_tuyen_bay_by_id(tuyen_bay_id):
    return db.session.query(TuyenBay).filter(TuyenBay.id == tuyen_bay_id).one_or_none()

def get_san_bay_by_id(san_bay_id):
    return db.session.query(SanBay).filter(SanBay.id == san_bay_id).one_or_none()


def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_customer_by_phone(sdt):
    return KhachHang.query.filter_by(sdt=sdt).first()

def register(name, username, password, avatar):
    try:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())  # Mã hóa mật khẩu với MD5
        u = User(user_role_id=3, name=name, username=username.strip(), password=password, anh_dai_dien=avatar)
        db.session.add(u)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Tên đăng nhập đã tồn tại")



def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def get_available_seats(may_bay_id, ticket_class):
    if ticket_class == 'hang_1':
        return GheMayBay.query.filter_by(may_bay_id=may_bay_id, hang_ghe='hang_1', trang_thai_ghe=False).all()
    else:
        return GheMayBay.query.filter_by(may_bay_id=may_bay_id, hang_ghe='hang_2', trang_thai_ghe=False).all()


def update_seat_status(ghes_id, status):
    """Cập nhật trạng thái ghế (chọn hoặc bỏ chọn)."""
    ghe = GheMayBay.query.get(ghes_id)
    if ghe:
        ghe.trang_thai_ghe = status
        db.session.commit()
    return ghe


from QuanLyChuyenBay import VN_PAY_CONFIG, MOMO_CONFIG



def momo_payment(flight_id, ticket_class):
    chuyen_bay = get_chuyen_bay_by_id(flight_id)
    if ticket_class == 'hang_1':
        gia_ve = chuyen_bay.gia_ve_hang_1
    else:
        gia_ve = chuyen_bay.gia_ve_hang_2

    endpoint = MOMO_CONFIG['endpoint']
    partner_code = MOMO_CONFIG['partner_code']
    access_key = MOMO_CONFIG['access_key']
    secret_key = MOMO_CONFIG['secret_key']
    order_info = "Thanh toan chuyen bay"
    return_url = MOMO_CONFIG['return_url']
    notify_url = MOMO_CONFIG['notify_url']
    order_id = str(int(time.time()))
    request_id = order_id
    amount = str(gia_ve)
    request_type = "captureMoMoWallet"
    extra_data = ""  # pass empty value if your merchant does not have stores

    raw_signature = f"partnerCode={partner_code}&accessKey={access_key}&requestId={request_id}&amount={amount}&orderId={order_id}&orderInfo={order_info}&returnUrl={return_url}&notifyUrl={notify_url}&extraData={extra_data}"

    signature = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest()

    data = {
        'partnerCode': partner_code,
        'accessKey': access_key,
        'requestId': request_id,
        'amount': amount,
        'orderId': order_id,
        'orderInfo': order_info,
        'returnUrl': return_url,
        'notifyUrl': notify_url,
        'extraData': extra_data,
        'requestType': request_type,
        'signature': signature
    }

    response = requests.post(endpoint, json=data)
    result = response.json()
    if result['errorCode'] == 0:
        return result['payUrl']
    else:
        raise Exception("Lỗi khi thanh toán với MoMo: " + result['localMessage'])

def vnpay_payment(flight_id, ticket_class):
    chuyen_bay = get_chuyen_bay_by_id(flight_id)
    if ticket_class == 'hang_1':
        gia_ve = chuyen_bay.gia_ve_hang_1
    else:
        gia_ve = chuyen_bay.gia_ve_hang_2

    vnp_TmnCode = VN_PAY_CONFIG['vnp_TmnCode']
    vnp_HashSecret = VN_PAY_CONFIG['vnp_HashSecret']
    vnp_Url = VN_PAY_CONFIG['vnp_Url']
    vnp_Returnurl = "http://127.0.0.1:5000/vnpay_return"
    vnp_TxnRef = str(int(time.time()))
    vnp_OrderInfo = "Thanh toan chuyen bay"
    vnp_Amount = str(gia_ve * 100)  # Số tiền thanh toán cần nhân với 100 (VD: 1,000 VND -> 100000)
    vnp_Locale = "vn"
    vnp_BankCode = ""
    vnp_IpAddr = request.remote_addr

    inputData = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Amount": vnp_Amount,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_OrderType": "other",
        "vnp_Locale": vnp_Locale,
        "vnp_ReturnUrl": vnp_Returnurl,
        "vnp_IpAddr": vnp_IpAddr
    }

    inputData = {k: v for k, v in sorted(inputData.items())}
    queryString = '&'.join(f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in inputData.items())
    hashData = '&'.join(f"{key}={value}" for key, value in inputData.items())
    vnp_SecureHash = hashlib.sha256((vnp_HashSecret + hashData).encode('utf-8')).hexdigest()
    paymentUrl = f"{vnp_Url}?{queryString}&vnp_SecureHashType=SHA256&vnp_SecureHash={vnp_SecureHash}"

    return paymentUrl


def get_customer_by_phone(sdt):
    return KhachHang.query.filter_by(sdt=sdt).first()

def create_customer(ten_khach_hang, cmnd_cccd, sdt):
    khach_hang_moi = KhachHang(
        ten_khach_hang=ten_khach_hang,
        cmnd_cccd=cmnd_cccd,
        sdt=sdt
    )
    db.session.add(khach_hang_moi)
    db.session.commit()
    return khach_hang_moi

def sell_ticket(khach_hang_id, chuyen_bay_id, hang_ghe, gia_ve, user_id):
    ve_moi = Ve(
        khach_hang_id=khach_hang_id,
        chuyen_bay_id=chuyen_bay_id,
        hoa_don_id=NULLTYPE,  # Điều này có thể cần thay đổi để phù hợp với hóa đơn thật
        user_id=user_id,
        ghe_id=NULLTYPE  # Cần có logic để lấy ghế có sẵn phù hợp

    )
    db.session.add(ve_moi)
    db.session.commit()
    return ve_moi
