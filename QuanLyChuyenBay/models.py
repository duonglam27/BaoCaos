import hashlib
from datetime import datetime
import math

from flask_admin import Admin
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship, backref
from enum import Enum as UserEnum
from enum import Enum as HangVeEnum
from enum import Enum as Sex
from QuanLyChuyenBay import db, app

from enum import Enum

class GioiTinhEnum(Enum):
    NAM = 'Nam'
    NU = 'Nu'
    KHAC = 'Khac'

# Bảng Role
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_role = db.Column(db.String(50), nullable=False)

# Bảng Sân bay
class SanBay(db.Model):
    __tablename__ = 'san_bay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_sb = db.Column(db.String(100), nullable=False)
    ten_khu_vuc = db.Column(db.String(100), nullable=False)

# Bảng Tuyến bay
class TuyenBay(db.Model):
    __tablename__ = 'tuyen_bay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    san_bay_di_id = db.Column(db.Integer, db.ForeignKey('san_bay.id'), nullable=False)
    san_bay_den_id = db.Column(db.Integer, db.ForeignKey('san_bay.id'), nullable=False)
    khoang_cach = db.Column(db.Float, nullable=False)
    thoi_gian_bay = db.Column(db.Integer, nullable=False)

    # Backref to easily access SanBay in the reverse direction
    san_bay_di = db.relationship('SanBay', foreign_keys=[san_bay_di_id], backref=backref('tuyen_bay_di', lazy=True))
    san_bay_den = db.relationship('SanBay', foreign_keys=[san_bay_den_id], backref=backref('tuyen_bay_den', lazy=True))

# Bảng Sân bay trung gian
class SanBayTrungGian(db.Model):
    __tablename__ = 'san_bay_trung_gian'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tuyen_bay_id = db.Column(db.Integer, db.ForeignKey('tuyen_bay.id'), nullable=False)
    san_bay_id = db.Column(db.Integer, db.ForeignKey('san_bay.id'), nullable=False)
    thu_tu_dung = db.Column(db.Integer, nullable=False)
    thoi_gian_dung = db.Column(db.Integer, nullable=False)
    ghi_chu = db.Column(db.String(255))

    # Backref for SanBay relationship
    tuyen_bay = db.relationship('TuyenBay', backref=backref('san_bay_trung_gian', lazy=True))
    san_bay = db.relationship('SanBay', backref=backref('san_bay_trung_gian', lazy=True))

# Bảng Máy bay
class MayBay(db.Model):
    __tablename__ = 'may_bay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_may_bay = db.Column(db.String(100), nullable=False)
    tinh_trang_hoat_dong = db.Column(db.Boolean, nullable=False)
    so_luong_hang_ghe_1 = db.Column(db.Integer, nullable=False)
    so_luong_hang_ghe_2 = db.Column(db.Integer, nullable=False)
    nam_san_xuat = db.Column(db.DateTime, nullable=False)


# Bảng Ghế máy bay
class GheMayBay(db.Model):
    __tablename__ = 'ghe_may_bay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    may_bay_id = db.Column(db.Integer, db.ForeignKey('may_bay.id'), nullable=False)
    ten_ghe = db.Column(db.String(10), nullable=False)
    hang_ghe = db.Column(db.String(10), nullable=False)
    trang_thai_ghe = db.Column(db.Boolean, nullable=False)

    # Backref to MayBay
    may_bay = db.relationship('MayBay', backref=db.backref('ghe_may_bays', lazy=True))

# Bảng Chuyến bay
class ChuyenBay(db.Model):
    __tablename__ = 'chuyen_bay'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_chuyen_bay = db.Column(db.String(100), nullable=False)
    tuyen_bay_id = db.Column(db.Integer, db.ForeignKey('tuyen_bay.id'), nullable=False)
    may_bay_id = db.Column(db.Integer, db.ForeignKey('may_bay.id'), nullable=False)
    ngay_gio_bay = db.Column(db.DateTime, nullable=False)
    gia_ve_hang_1 = db.Column(db.Float, nullable=False)
    gia_ve_hang_2 = db.Column(db.Float, nullable=False)

    # Backref to TuyenBay
    tuyen_bay = db.relationship('TuyenBay', backref=backref('chuyen_bay', lazy=True))
    may_bay = db.relationship('MayBay', backref=db.backref('chuyen_bay', lazy=True))


# Bảng Khách hàng
class KhachHang(db.Model):
    __tablename__ = 'khach_hang'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_khach_hang = db.Column(db.String(100), nullable=False)
    sdt = db.Column(db.String(10), nullable=False)
    CCCD=db.Column(db.String(12),unique=True, nullable=False)




# Bảng Vé
class Ve(db.Model):
    __tablename__ = 've'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    khach_hang_id = db.Column(db.Integer, db.ForeignKey('khach_hang.id'), nullable=False)
    chuyen_bay_id = db.Column(db.Integer, db.ForeignKey('chuyen_bay.id'), nullable=False)
    hoa_don_id = db.Column(db.Integer, db.ForeignKey('hoa_don.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ghe_id = db.Column(db.Integer, db.ForeignKey('ghe_may_bay.id'), nullable=False)

    # Backref to ChuyenBay
    chuyen_bay = db.relationship('ChuyenBay', backref=backref('ve', lazy=True))
    khach_hang = db.relationship('KhachHang', backref=backref('khach_hang', lazy=True))


# Bảng Hóa đơn
class HoaDon(db.Model):
    __tablename__ = 'hoa_don'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngay_thanh_toan = db.Column(db.DateTime, nullable=False)
    tong_tien = db.Column(db.Float, nullable=False)
    phuong_thuc_thanh_toan = db.Column(db.String(50), nullable=False)


# Bảng User
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    user_role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    anh_dai_dien = db.Column(db.String(255), nullable=True)

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    # Backref for Ve relationship (User can have many tickets)
    ve = db.relationship('Ve', backref=backref('user', lazy=True))

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.user_role_id == 1

    def is_staff(self):
        return self.user_role_id == 2

    def is_user(self):
        return self.user_role_id == 3


if __name__ == '__main__':
        with app.app_context():

        # db.drop_all()

            db.create_all()



            # Tạo dữ liệu mẫu cho bảng Role
            # role1 = Role(ten_role="Admin")
            # role2 = Role(ten_role="User")
            # role3 = Role(ten_role="Guest")
            # db.session.add_all([role1, role2, role3])

            # Tạo dữ liệu mẫu cho bảng User
            password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
            user1 = User(name="admin", username="20", password=password, user_role_id=1)
            user2 = User(name="Staff", username="4", password=password, user_role_id=2)
            user3 = User(name="NGdung", username="5", password=password, user_role_id=3)

            db.session.add_all([user1, user2, user3])


        # db.session.add_all([user1, user2, user3])
            #
            # # Tạo dữ liệu mẫu cho bảng SanBay
            # san_bay_1 = SanBay(ten_sb="Tan Son Nhat", ten_khu_vuc="Ho Chi Minh")
            # san_bay_2 = SanBay(ten_sb="Noi Bai", ten_khu_vuc="Ha Noi")
            # san_bay_3 = SanBay(ten_sb="Da Nang", ten_khu_vuc="Da Nang")
            # db.session.add_all([san_bay_1, san_bay_2, san_bay_3])

            # # Tạo dữ liệu mẫu cho bảng TuyenBay
            # tuyen_bay_1 = TuyenBay(san_bay_di_id=1, san_bay_den_id=2, khoang_cach=1150.0, thoi_gian_bay=120)
            # tuyen_bay_2 = TuyenBay(san_bay_di_id=2, san_bay_den_id=3, khoang_cach=800.0, thoi_gian_bay=90)
            # tuyen_bay_3 = TuyenBay(san_bay_di_id=3, san_bay_den_id=1, khoang_cach=850.0, thoi_gian_bay=100)
            # db.session.add_all([tuyen_bay_1, tuyen_bay_2, tuyen_bay_3])

            # # Tạo dữ liệu mẫu cho bảng SanBayTrungGian
            # san_bay_trung_gian_1 = SanBayTrungGian(tuyen_bay_id=1, san_bay_id=1, thu_tu_dung=1, thoi_gian_dung=30,
            #                                        ghi_chu="Dung de tiep nhien lieu")
            # san_bay_trung_gian_2 = SanBayTrungGian(tuyen_bay_id=2, san_bay_id=2, thu_tu_dung=1, thoi_gian_dung=25,
            #                                        ghi_chu="Dung de tiep nhien lieu")
            # san_bay_trung_gian_3 = SanBayTrungGian(tuyen_bay_id=3, san_bay_id=3, thu_tu_dung=1, thoi_gian_dung=35,
            #                                        ghi_chu="Dung de tiep nhien lieu")
            # db.session.add_all([san_bay_trung_gian_1, san_bay_trung_gian_2, san_bay_trung_gian_3])
            #
            # # Tạo dữ liệu mẫu cho bảng MayBay
            # may_bay_1 = MayBay(ten_may_bay="Boeing 737", tinh_trang_hoat_dong=True, so_luong_hang_ghe_1=20,
            #                    so_luong_hang_ghe_2=80, nam_san_xuat=datetime(2015, 5, 21))
            # may_bay_2 = MayBay(ten_may_bay="Airbus A320", tinh_trang_hoat_dong=True, so_luong_hang_ghe_1=30,
            #                    so_luong_hang_ghe_2=100, nam_san_xuat=datetime(2018, 7, 15))
            # may_bay_3 = MayBay(ten_may_bay="Boeing 777", tinh_trang_hoat_dong=True, so_luong_hang_ghe_1=40,
            #                    so_luong_hang_ghe_2=200, nam_san_xuat=datetime(2020, 1, 12))
            # db.session.add_all([may_bay_1, may_bay_2, may_bay_3])
            #
            # # Tạo dữ liệu mẫu cho bảng GheMayBay
            # ghe_may_bay_1 = GheMayBay(may_bay_id=1, ten_ghe="1A", hang_ghe="Thương gia", trang_thai_ghe=False)
            # ghe_may_bay_2 = GheMayBay(may_bay_id=1, ten_ghe="2A", hang_ghe="Thương gia", trang_thai_ghe=False)
            # ghe_may_bay_3 = GheMayBay(may_bay_id=1, ten_ghe="3A", hang_ghe="Thương gia", trang_thai_ghe=False)
            # db.session.add_all([ghe_may_bay_1, ghe_may_bay_2, ghe_may_bay_3])

            # # # Tạo dữ liệu mẫu cho bảng ChuyenBay
            # chuyen_bay_1 = ChuyenBay(ten_chuyen_bay="AV123", tuyen_bay_id=1, may_bay_id=1,
            #                          ngay_gio_bay=datetime(2024, 5, 15, 10, 0), gia_ve_hang_1=2000000.0,
            #                          gia_ve_hang_2=1000000.0)
            # chuyen_bay_2 = ChuyenBay(ten_chuyen_bay="VN456", tuyen_bay_id=2, may_bay_id=2,
            #                          ngay_gio_bay=datetime(2024, 5, 21, 12, 0), gia_ve_hang_1=3000000.0,
            #                          gia_ve_hang_2=1500000.0)
            # chuyen_bay_3 = ChuyenBay(ten_chuyen_bay="VN789", tuyen_bay_id=3, may_bay_id=3,
            #                          ngay_gio_bay=datetime(2024, 6, 22, 14, 0), gia_ve_hang_1=4000000.0,
            #                          gia_ve_hang_2=2000000.0)
            # db.session.add_all([chuyen_bay_1, chuyen_bay_2, chuyen_bay_3])

            # Tạo dữ liệu mẫu cho bảng KhachHang
            # khach_hang_1 = KhachHang(ten_khach_hang="Tran Van C", sdt="0123456789",
            #                          CCCD="123456789012")
            # khach_hang_2 = KhachHang(ten_khach_hang="Tran Van ADDAS", sdt="0123456789",
            #                      CCCD="210987456321")
            # khach_hang_3 = KhachHang(ten_khach_hang="Lê Van A", sdt="0123456789",
            #                      CCCD="125478785412")
            # db.session.add_all([khach_hang_1, khach_hang_2, khach_hang_3])

            # ve_1 = Ve(khach_hang_id=4, chuyen_bay_id=1, user_id=1, ghe_id=1, hoa_don_id=1)
            # ve_2 = Ve(khach_hang_id=5, chuyen_bay_id=2, user_id=2, ghe_id=2, hoa_don_id=2)
            # ve_3 = Ve(khach_hang_id=6, chuyen_bay_id=3, user_id=3, ghe_id=3, hoa_don_id=3)
            # db.session.add_all([ve_1, ve_2, ve_3])

            # Tạo dữ liệu mẫu cho bảng HoaDon
            # hoa_don_1 = HoaDon( ngay_thanh_toan=datetime(2024, 5, 1), tong_tien=2000000.0,
            #                    phuong_thuc_thanh_toan="Tiền mặt")
            # hoa_don_2 = HoaDon( ngay_thanh_toan=datetime(2024, 5, 1), tong_tien=1000000.0,
            #                    phuong_thuc_thanh_toan="Thẻ tín dụng")
            # hoa_don_3 = HoaDon( ngay_thanh_toan=datetime(2024, 6, 10), tong_tien=2500000.0,
            #                    phuong_thuc_thanh_toan="Chuyển khoản")
            # db.session.add_all([hoa_don_1, hoa_don_2, hoa_don_3])
            db.session.commit()