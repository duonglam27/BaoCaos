import json
import math
import re
import urllib
import uuid

import requests
from flask import request
from flask_sqlalchemy.session import Session
from oauthlib.uri_validate import query
from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy.sql.sqltypes import NULLTYPE

from QuanLyChuyenBay.models import ChuyenBay, TuyenBay, SanBay, User, SanBayTrungGian, HangGheChuyenBay
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
import hashlib
from sqlalchemy.exc import IntegrityError
from QuanLyChuyenBay import db
from QuanLyChuyenBay.models import User, Role




def get_user_by_id(user_id):
    return User.query.get(user_id)





def register(name, username, password, anh_dai_dien):
    try:
        # Hash the password using MD5
        hashed_password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        # Create a new user instance
        u = User(name=name, username=username.strip(), password=hashed_password, user_role=Role.USER,
                 anh_dai_dien=anh_dai_dien)

        # Add and commit the new user to the database
        db.session.add(u)
        db.session.commit()
    except IntegrityError:
        # Rollback the session in case of an IntegrityError (e.g., duplicate username)
        db.session.rollback()
        raise ValueError("Tên đăng nhập đã tồn tại")
    except Exception as e:
        # Rollback the session for any other exceptions and re-raise the exception
        db.session.rollback()
        raise e





def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()



def load_chuyen_bay():
    try:
        chuyen_bay_list = ChuyenBay.query.all()
        return chuyen_bay_list
    except Exception as e:
        print(f"Error loading flights: {e}")
        return []

def load_san_bay():
    try:
        san_bay_list = SanBay.query.all()
        return san_bay_list
    except Exception as e:
        print(f"Error loading san bay: {e}")
        return []

def load_chuyen_bay_theo_tinh_trang():
    try:
        chuyen_bay_con_trong = ChuyenBay.query.filter_by(tinh_trang=True).all()
        return chuyen_bay_con_trong
    except Exception as e:
        print(f"Error loading chuyen bay con trong: {e}")
        return []


def load_hang_ghe_theo_id(chuyen_bay_id=None):
    try:
        hang_ghe = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay_id).all()
        return hang_ghe
    except Exception as e:
        print(f"Error loading chuyen bay con trong: {e}")
        return []
















