import hashlib

from click import DateTime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from QuanLyChuyenBay import app, db

class QuyDinhHeThong(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    soLuongSanBay = db.Column(db.Integer, nullable=False, default=10)  # Thêm cột và default value
    thoiGianBayToiThieu = db.Column(db.Integer, nullable=False, default=30)
    soLuongSanBayTrungGian = db.Column(db.Integer, nullable=False, default=2)
    thoiGianDungToiThieu = db.Column(db.Integer, nullable=False, default=20)
    thoiGianDungToiDa = db.Column(db.Integer, nullable=False, default=30)
    thoiGianDatVe = db.Column(db.Integer, nullable=False, default=12)
    thoiGianBanVe = db.Column(db.Integer, nullable=False, default=4)

class Role(Enum):
    ADMIN = 'admin'
    NV = 'nhan vien'
    USER = 'user'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Enum(Role), nullable=False)
    anh_dai_dien = db.Column(db.String(255), nullable=True)

    users = relationship('DatVe', backref='user', lazy=True)

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
        return self.user_role == Role.ADMIN

    def is_staff(self):
        return self.user_role == Role.NV

    def is_user(self):
        return self.user_role == Role.USER


class HangGhe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_hang_ghe = db.Column(db.String(100), nullable=False)
    gia=db.Column(db.Integer,nullable=False)

    hang_ghes = relationship('HangGheChuyenBay', backref='hang_ghe', lazy=True)

class SanBay(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_sb = db.Column(db.String(100), nullable=False)

    san_bays = relationship('SanBayTrungGian', backref='chuyen_bay', lazy=True)

class TuyenBay(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_tuyen_bay = db.Column(db.String(50), nullable=False)

    tuyen_bays=relationship('ChuyenBay',backref='tuyen_bay',lazy=True)


class ChuyenBay(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_chuyen_bay = db.Column(db.String(100), nullable=False)
    tuyen_bay_id = db.Column(db.Integer, db.ForeignKey(TuyenBay.id), nullable=False)
    ngay_bay=db.Column(db.DateTime,nullable=False)
    tinh_trang = db.Column(db.Boolean, nullable=False)

    chuyen_bay_dat_ves = relationship('DatVe', backref='chuyen_bay_dat_ve', lazy=True)
    chuyen_bay_hang_ghe_chuyen_bays = relationship('HangGheChuyenBay', backref='chuyen_bay_hang_ghe', lazy=True)
    chuyen_bay_san_bay_trung_gians = relationship('SanBayTrungGian', backref='chuyen_bay_san_bay_trung_gian', lazy=True)  # Sửa backref ở đây

class SanBayTrungGian(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tuyen_bay_id = db.Column(db.Integer, db.ForeignKey(ChuyenBay.id), nullable=False)
    san_bay_id = db.Column(db.Integer, db.ForeignKey(SanBay.id), nullable=False)
    thoi_gian_dung=db.Column(db.Integer,nullable=False)
    ghi_chu= db.Column(db.String(100),nullable=True)


class HangGheChuyenBay(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    hang_ghe_id = db.Column(db.Integer, db.ForeignKey(HangGhe.id), nullable=False)
    chuyen_bay_id = db.Column(db.Integer, db.ForeignKey(ChuyenBay.id), nullable=False)
    so_luong_ghe=db.Column(db.Integer,nullable=False)


    hang_ghe_dat_ve=relationship('DatVe',backref='hang_ghe_dat_ve',lazy=True)

class DatVe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chuyen_bay_id = db.Column(db.Integer, db.ForeignKey(ChuyenBay.id), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    ten_hanh_khach=db.Column(db.String(100),nullable=False)
    cccd = db.Column(db.String(100), nullable=False)
    sdt = db.Column(db.String(100), nullable=False)
    hang_ghe_chuyen_bay_id = db.Column(db.Integer, db.ForeignKey(HangGheChuyenBay.id),
                                       nullable=False)  # Khóa ngoại đến HangGheChuyenBay

    hoa_dons = relationship('HoaDon', backref='hoa_don', lazy=True)

class HoaDon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dat_ve_id = db.Column(db.Integer, db.ForeignKey(DatVe.id), nullable=False)
    tong_tien=db.Column(db.Float,nullable=False)
    ngay_thanh_toan=db.Column(db.DateTime,nullable=False)
    trang_thai_hoa_don = db.Column(db.Boolean, nullable=False)






def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()







with app.app_context():
    db.drop_all()
    db.create_all()
    quy_dinh_mau = QuyDinhHeThong(
        soLuongSanBay=10,
        thoiGianBayToiThieu=30,
        soLuongSanBayTrungGian=2,
        thoiGianDungToiThieu=20,
        thoiGianDungToiDa=30,
        thoiGianDatVe=12,
        thoiGianBanVe=4
    )

    # Thêm dữ liệu vào cơ sở dữ liệu
    db.session.add(quy_dinh_mau)
    db.session.commit()
    # Tạo dữ liệu mẫu cho bảng User
    users = [
        User(name="User 1", username="user1", password=hash_password("password1"), user_role=Role.ADMIN, anh_dai_dien="default.jpg"),
        User(name="User 2", username="user2", password=hash_password("password2"), user_role=Role.NV, anh_dai_dien="default.jpg"),
        User(name="User 3", username="user3", password=hash_password("password3"), user_role=Role.USER, anh_dai_dien="default.jpg"),
        User(name="User 4", username="user4", password=hash_password("password4"), user_role=Role.USER, anh_dai_dien="default.jpg"),
        User(name="User 5", username="user5", password=hash_password("password5"), user_role=Role.USER, anh_dai_dien="default.jpg")
    ]
    db.session.add_all(users)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng HangGhe
    hang_ghes = [
        HangGhe(ten_hang_ghe="ThuongGia", gia=1000),
        HangGhe(ten_hang_ghe="CoBan", gia=500),
        HangGhe(ten_hang_ghe="Economy", gia=300),
        HangGhe(ten_hang_ghe="Business", gia=700),
        HangGhe(ten_hang_ghe="FirstClass", gia=1200)
    ]
    db.session.add_all(hang_ghes)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng SanBay
    san_bays = [
        SanBay(ten_sb="Noi Bai International Airport"),
        SanBay(ten_sb="Tan Son Nhat International Airport"),
        SanBay(ten_sb="Da Nang International Airport"),
        SanBay(ten_sb="Phu Bai International Airport"),
        SanBay(ten_sb="Cat Bi International Airport")
    ]
    db.session.add_all(san_bays)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng TuyenBay
    tuyen_bays = [
        TuyenBay(ten_tuyen_bay="Hanoi to Ho Chi Minh City"),
        TuyenBay(ten_tuyen_bay="Hanoi to Da Nang"),
        TuyenBay(ten_tuyen_bay="Ho Chi Minh City to Da Nang"),
        TuyenBay(ten_tuyen_bay="Da Nang to Hue"),
        TuyenBay(ten_tuyen_bay="Ho Chi Minh City to Hue")
    ]
    db.session.add_all(tuyen_bays)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng ChuyenBay
    chuyen_bays = [
        ChuyenBay(ten_chuyen_bay="VN001", tuyen_bay_id=1, ngay_bay=datetime(2024, 12, 31, 8, 0), tinh_trang=True),
        ChuyenBay(ten_chuyen_bay="VN002", tuyen_bay_id=2, ngay_bay=datetime(2024, 12, 31, 12, 0), tinh_trang=True),
        ChuyenBay(ten_chuyen_bay="VN003", tuyen_bay_id=3, ngay_bay=datetime(2024, 12, 31, 16, 0), tinh_trang=True),
        ChuyenBay(ten_chuyen_bay="VN004", tuyen_bay_id=4, ngay_bay=datetime(2024, 12, 31, 20, 0), tinh_trang=True),
        ChuyenBay(ten_chuyen_bay="VN005", tuyen_bay_id=5, ngay_bay=datetime(2025, 1, 1, 0, 0), tinh_trang=True)
    ]
    db.session.add_all(chuyen_bays)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng HangGheChuyenBay
    hang_ghe_chuyen_bays = [
        HangGheChuyenBay(hang_ghe_id=1, chuyen_bay_id=1, so_luong_ghe=100),
        HangGheChuyenBay(hang_ghe_id=2, chuyen_bay_id=1, so_luong_ghe=150),
        HangGheChuyenBay(hang_ghe_id=3, chuyen_bay_id=2, so_luong_ghe=200),
        HangGheChuyenBay(hang_ghe_id=4, chuyen_bay_id=2, so_luong_ghe=100),
        HangGheChuyenBay(hang_ghe_id=5, chuyen_bay_id=4, so_luong_ghe=50)
    ]
    db.session.add_all(hang_ghe_chuyen_bays)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng DatVe
    dat_ves = [
        DatVe(chuyen_bay_id=1, user_id=1, ten_hanh_khach="Hanh Khach 1", cccd="123456789", sdt="0987654321", hang_ghe_chuyen_bay_id=1),
        DatVe(chuyen_bay_id=1, user_id=2, ten_hanh_khach="Hanh Khach 2", cccd="987654321", sdt="0123456789", hang_ghe_chuyen_bay_id=2),
        DatVe(chuyen_bay_id=2, user_id=3, ten_hanh_khach="Hanh Khach 3", cccd="223344556", sdt="0912345678", hang_ghe_chuyen_bay_id=3),
        DatVe(chuyen_bay_id=3, user_id=4, ten_hanh_khach="Hanh Khach 4", cccd="445566778", sdt="0901234567", hang_ghe_chuyen_bay_id=4),
        DatVe(chuyen_bay_id=4, user_id=5, ten_hanh_khach="Hanh Khach 5", cccd="556677889", sdt="0998765432", hang_ghe_chuyen_bay_id=5)
    ]
    db.session.add_all(dat_ves)
    db.session.commit()

    # Tạo dữ liệu mẫu cho bảng HoaDon
    hoa_dons = [
        HoaDon(dat_ve_id=1, tong_tien=1000.0, ngay_thanh_toan=datetime(2024, 12, 25), trang_thai_hoa_don=True),
        HoaDon(dat_ve_id=2, tong_tien=500.0, ngay_thanh_toan=datetime(2024, 12, 26), trang_thai_hoa_don=True),
        HoaDon(dat_ve_id=3, tong_tien=300.0, ngay_thanh_toan=datetime(2024, 12, 27), trang_thai_hoa_don=True),
        HoaDon(dat_ve_id=4, tong_tien=700.0, ngay_thanh_toan=datetime(2024, 12, 28), trang_thai_hoa_don=True),
        HoaDon(dat_ve_id=5, tong_tien=1200.0, ngay_thanh_toan=datetime(2024, 12, 29), trang_thai_hoa_don=True)
    ]
    db.session.add_all(hoa_dons)
    db.session.commit()

    print("Sample data has been added successfully.")
