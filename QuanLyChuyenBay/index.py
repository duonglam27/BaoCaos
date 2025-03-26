from sqlalchemy import func

from QuanLyChuyenBay import login, utils, db
from flask import render_template, request, redirect, session, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template
import cloudinary.uploader
from QuanLyChuyenBay import app, dao, models
from QuanLyChuyenBay.dao import load_chuyen_bay, load_san_bay, load_chuyen_bay_theo_tinh_trang, load_hang_ghe_theo_id
from QuanLyChuyenBay.models import ChuyenBay, DatVe, HangGheChuyenBay, SanBay, SanBayTrungGian, TuyenBay, \
    QuyDinhHeThong, User, HangGhe, HoaDon
from flask import render_template, request

from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange



@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/', methods=['GET', 'POST'])
def home():
    san_bay_id = request.args.get("san_bay")
    ngay_bay = request.args.get("ngay_bay")
    if san_bay_id or ngay_bay:
        return redirect(url_for('chuyenbaylistactive', san_bay=san_bay_id, ngay_bay=ngay_bay))

    sanbays = load_san_bay()

    return render_template('index.html', san_bay=san_bay_id, ngay_bay=ngay_bay, sanbays=sanbays)


@app.route('/timchuyenbay', methods=['GET', 'POST'])
@login_required
def timchuyenbay():
    if request.method == 'POST':
        ten_chuyen_bay = request.form.get('ten_chuyen_bay')
        ngay_bay = request.form.get('ngay_bay')
        chuyen_bays = []

        if ten_chuyen_bay:
            # Tìm kiếm chuyến bay dựa trên tên chuyến bay
            chuyen_bays = ChuyenBay.query.filter(
                ChuyenBay.ten_chuyen_bay.like(f"%{ten_chuyen_bay}%")
            ).all()

        elif ngay_bay:
            try:
                ngay_bay_date = datetime.strptime(ngay_bay, '%Y-%m-%d').date()
                # Tìm kiếm chuyến bay dựa trên ngày bay
                chuyen_bays = ChuyenBay.query.filter(
                    db.func.date(ChuyenBay.ngay_bay) == ngay_bay_date
                ).all()
            except ValueError:
                flash('Định dạng ngày bay không hợp lệ.', 'danger')
                return render_template('timchuyenbay.html')

        return render_template('ketquatimkiem.html', chuyen_bays=chuyen_bays)

    return render_template('timchuyenbay.html')


from datetime import datetime

@app.route('/thanhtoan/<int:chuyen_bay_id>', methods=['GET', 'POST'])
@login_required
def thanhtoan(chuyen_bay_id):
    chuyen_bay = ChuyenBay.query.get_or_404(chuyen_bay_id)
    hang_ghe_chuyen_bays = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay_id).all()

    # Truy vấn giá trị giờ từ bảng QuyDinhChuyenBay
    quydinh = QuyDinhHeThong.query.first()
    thoi_gian_dat = QuyDinhHeThong.thoiGianDatVe

    # Kiểm tra thời gian hiện tại và thời gian bay
    current_time = datetime.utcnow()
    time_difference = chuyen_bay.ngay_bay - current_time

    if time_difference < timedelta(hours=12):
        flash(f'Chỉ có thể thanh toán các chuyến bay trước {thoi_gian_dat} giờ kể từ ngày bay.', 'danger')
        return redirect(url_for('lichchuyenbay'))

    if request.method == 'POST':
        ten_hanh_khach = request.form.get('ten_hanh_khach')
        cccd = request.form.get('cccd')
        sdt = request.form.get('sdt')
        hang_ghe_chuyen_bay_id = request.form.get('hang_ghe_chuyen_bay_id')

        hang_ghe_chuyen_bay = HangGheChuyenBay.query.get(hang_ghe_chuyen_bay_id)
        gia_ve = hang_ghe_chuyen_bay.hang_ghe.gia

        # Kiểm tra số lượng ghế còn lại
        if hang_ghe_chuyen_bay.so_luong_ghe <= 0:
            flash('Hạng ghế đã hết chỗ.', 'danger')
            return render_template('thanhtoan.html', chuyen_bay=chuyen_bay, hang_ghe_chuyen_bays=hang_ghe_chuyen_bays)

        # Trừ số lượng ghế
        hang_ghe_chuyen_bay.so_luong_ghe -= 1
        db.session.add(hang_ghe_chuyen_bay)

        # Lưu thông tin vào bảng Ve
        ve_moi = DatVe(
            chuyen_bay_id=chuyen_bay_id,
            user_id=current_user.id,
            ten_hanh_khach=ten_hanh_khach,
            cccd=cccd,
            sdt=sdt,
            hang_ghe_chuyen_bay_id=hang_ghe_chuyen_bay_id,
        )
        db.session.add(ve_moi)
        db.session.commit()

        # Tạo hóa đơn sau khi thanh toán thành công
        hoa_don = HoaDon(
            dat_ve_id=ve_moi.id,
            tong_tien=gia_ve,  # Có thể tính tổng tiền ở đây nếu có nhiều yếu tố khác
            ngay_thanh_toan = datetime.utcnow(),  # Lưu ngày thanh toán
            trang_thai_hoa_don = 1  # Đặt trạng thái là 'Đã thanh toán'
        )
        db.session.add(hoa_don)
        db.session.commit()

        flash('Thanh toán thành công và hóa đơn đã được tạo!', 'success')
        return redirect(url_for('timchuyenbay'))

    return render_template('thanhtoan.html', chuyen_bay=chuyen_bay, hang_ghe_chuyen_bays=hang_ghe_chuyen_bays)


@app.route('/themchuyenbay', methods=['GET', 'POST'])
@login_required
def themchuyenbay():
    # Truy vấn danh sách các sân bay từ cơ sở dữ liệu
    san_bays = SanBay.query.all()
    hang_ghes = HangGhe.query.all()

    if request.method == 'POST':
        ma_chuyen_bay = request.form.get('ma_chuyen_bay')
        san_bay_di = request.form.get('san_bay_di')
        san_bay_den = request.form.get('san_bay_den')
        ngay_gio = request.form.get('ngay_gio')
        thoi_gian_bay = request.form.get('thoi_gian_bay')
        hang_ghe_1 = request.form.get('hang_ghe_1')
        so_luong_ghe_1 = request.form.get(
            'so_luong_ghe_1') or None  # Cho phép giá trị None để biểu thị không giới hạn ghế
        hang_ghe_2 = request.form.get('hang_ghe_2')
        so_luong_ghe_2 = request.form.get(
            'so_luong_ghe_2') or None  # Cho phép giá trị None để biểu thị không giới hạn ghế

        # Chuyển đổi ngày giờ thành datetime
        ngay_gio = datetime.strptime(ngay_gio, '%Y-%m-%dT%H:%M')

        # Tạo chuyến bay mới
        chuyen_bay = ChuyenBay(
            tuyen_bay_id=1,
            ten_chuyen_bay=ma_chuyen_bay,
            san_bay_di_id=san_bay_di,
            san_bay_den_id=san_bay_den,
            ngay_bay=ngay_gio,
            thoi_gian_bay=thoi_gian_bay
        )
        db.session.add(chuyen_bay)
        db.session.commit()

        # Thêm hạng ghế
        hang_ghe_chuyen_bay_1 = HangGheChuyenBay(
            chuyen_bay_id=chuyen_bay.id,
            hang_ghe_id=hang_ghe_1,
            so_luong_ghe=so_luong_ghe_1
        )
        hang_ghe_chuyen_bay_2 = HangGheChuyenBay(
            chuyen_bay_id=chuyen_bay.id,
            hang_ghe_id=hang_ghe_2,
            so_luong_ghe=so_luong_ghe_2
        )
        db.session.add(hang_ghe_chuyen_bay_1)
        db.session.add(hang_ghe_chuyen_bay_2)

        # Thêm sân bay trung gian nếu có
        for i in range(1, 3):
            san_bay_trung_gian = request.form.get(f'san_bay_trung_gian_{i}')
            thoi_gian_dung = request.form.get(f'thoi_gian_dung_{i}')
            ghi_chu = request.form.get(f'ghi_chu_{i}')

            if san_bay_trung_gian and thoi_gian_dung:
                san_bay_trung_gian_moi = SanBayTrungGian(
                    chuyen_bay_id=chuyen_bay.id,
                    san_bay_id=san_bay_trung_gian,
                    thoi_gian_dung=thoi_gian_dung,
                    ghi_chu=ghi_chu
                )
                db.session.add(san_bay_trung_gian_moi)

        db.session.commit()

        flash('Thêm chuyến bay thành công!', 'success')
        return redirect(url_for('home'))

    return render_template('themchuyenbay.html', san_bays=san_bays, hang_ghes=hang_ghes)

@app.route('/sua_chuyen_bay/<int:chuyen_bay_id>', methods=['GET', 'POST'])
@login_required
def sua_chuyen_bay(chuyen_bay_id):
    # Truy vấn chuyến bay cần sửa
    chuyen_bay = ChuyenBay.query.get_or_404(chuyen_bay_id)

    # Truy vấn danh sách sân bay và hạng ghế
    san_bays = SanBay.query.all()
    hang_ghes = HangGhe.query.all()

    if request.method == 'POST':
        # Lấy thông tin từ form
        ma_chuyen_bay = request.form.get('ma_chuyen_bay')
        san_bay_di = request.form.get('san_bay_di')
        san_bay_den = request.form.get('san_bay_den')
        ngay_gio = request.form.get('ngay_gio')
        thoi_gian_bay = request.form.get('thoi_gian_bay')
        hang_ghe_1 = request.form.get('hang_ghe_1')
        so_luong_ghe_1 = request.form.get('so_luong_ghe_1') or None
        hang_ghe_2 = request.form.get('hang_ghe_2')
        so_luong_ghe_2 = request.form.get('so_luong_ghe_2') or None

        # Chuyển đổi ngày giờ thành datetime
        ngay_gio = datetime.strptime(ngay_gio, '%Y-%m-%dT%H:%M')

        # Cập nhật thông tin chuyến bay
        chuyen_bay.ten_chuyen_bay = ma_chuyen_bay
        chuyen_bay.san_bay_di_id = san_bay_di
        chuyen_bay.san_bay_den_id = san_bay_den
        chuyen_bay.ngay_bay = ngay_gio
        chuyen_bay.thoi_gian_bay = thoi_gian_bay
        db.session.commit()

        # Cập nhật hạng ghế
        hang_ghe_chuyen_bay_1 = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay.id, hang_ghe_id=hang_ghe_1).first()
        if not hang_ghe_chuyen_bay_1:
            hang_ghe_chuyen_bay_1 = HangGheChuyenBay(chuyen_bay_id=chuyen_bay.id, hang_ghe_id=hang_ghe_1)
            db.session.add(hang_ghe_chuyen_bay_1)
        hang_ghe_chuyen_bay_1.so_luong_ghe = so_luong_ghe_1

        hang_ghe_chuyen_bay_2 = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay.id, hang_ghe_id=hang_ghe_2).first()
        if not hang_ghe_chuyen_bay_2:
            hang_ghe_chuyen_bay_2 = HangGheChuyenBay(chuyen_bay_id=chuyen_bay.id, hang_ghe_id=hang_ghe_2)
            db.session.add(hang_ghe_chuyen_bay_2)
        hang_ghe_chuyen_bay_2.so_luong_ghe = so_luong_ghe_2

        # Cập nhật sân bay trung gian
        for i in range(1, 3):
            san_bay_trung_gian = request.form.get(f'san_bay_trung_gian_{i}')
            thoi_gian_dung = request.form.get(f'thoi_gian_dung_{i}')
            ghi_chu = request.form.get(f'ghi_chu_{i}')

            san_bay_trung_gian_moi = SanBayTrungGian.query.filter_by(chuyen_bay_id=chuyen_bay.id, san_bay_id=san_bay_trung_gian).first()
            if san_bay_trung_gian_moi:
                san_bay_trung_gian_moi.thoi_gian_dung = thoi_gian_dung
                san_bay_trung_gian_moi.ghi_chu = ghi_chu
            elif san_bay_trung_gian and thoi_gian_dung:  # Thêm mới nếu không tồn tại
                san_bay_trung_gian_moi = SanBayTrungGian(
                    chuyen_bay_id=chuyen_bay.id,
                    san_bay_id=san_bay_trung_gian,
                    thoi_gian_dung=thoi_gian_dung,
                    ghi_chu=ghi_chu
                )
                db.session.add(san_bay_trung_gian_moi)

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()

        flash('Sửa chuyến bay thành công!', 'success')
        return redirect(url_for('dschuyenbayall'))

    return render_template('sua_chuyen_bay.html', chuyen_bay=chuyen_bay, san_bays=san_bays, hang_ghes=hang_ghes)



@app.route('/xoa_chuyen_bay/<int:chuyen_bay_id>', methods=['POST'])
@login_required
def xoa_chuyen_bay(chuyen_bay_id):
    # Truy vấn chuyến bay cần xóa
    chuyen_bay = ChuyenBay.query.get_or_404(chuyen_bay_id)

    # Xóa các bản ghi liên quan (hạng ghế, sân bay trung gian, etc.)
    hang_ghe_chuyen_bays = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay.id).all()
    for hang_ghe_chuyen_bay in hang_ghe_chuyen_bays:
        db.session.delete(hang_ghe_chuyen_bay)

    san_bay_trung_gians = SanBayTrungGian.query.filter_by(chuyen_bay_id=chuyen_bay.id).all()
    for san_bay_trung_gian in san_bay_trung_gians:
        db.session.delete(san_bay_trung_gian)

    # Sau khi xóa các bản ghi liên quan, xóa chuyến bay chính
    db.session.delete(chuyen_bay)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()

    flash('Chuyến bay đã được xóa thành công!', 'success')
    return redirect(url_for('dschuyenbayall'))  # Chuyển hướng về danh sách chuyến bay



@app.route('/dschuyenbayall', methods=['GET'])
def dschuyenbayall():
    # Lấy tất cả các chuyến bay từ cơ sở dữ liệu
    chuyen_bays = ChuyenBay.query.all()

    # Render trang dschuyenbayall và truyền danh sách chuyến bay vào template
    return render_template('dschuyenbayall.html', chuyen_bays=chuyen_bays)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Lấy giá trị tháng và năm từ form
        thang = request.form['thang']
        nam = request.form['nam']
        return bao_cao_doanh_thu_theo_thang(thang, nam)

    return render_template('index.html')


@app.route('/baocaodoanhthu/<int:thang>/<int:nam>', methods=['GET'])
@login_required
def bao_cao_doanh_thu_theo_thang(thang, nam):
    # Lấy dữ liệu doanh thu theo tuyến bay từ database
    doanh_thu_theo_tuyen = db.session.query(
        TuyenBay.ten_tuyen_bay,
        func.sum(HoaDon.tong_tien).label('doanh_thu'),
        func.count(ChuyenBay.id).label('so_luot_bay')
    ).join(ChuyenBay, TuyenBay.id == ChuyenBay.tuyen_bay_id) \
        .join(DatVe, ChuyenBay.id == DatVe.chuyen_bay_id) \
        .join(HoaDon, DatVe.id == HoaDon.dat_ve_id) \
        .filter(func.extract('month', HoaDon.ngay_thanh_toan) == thang) \
        .filter(func.extract('year', HoaDon.ngay_thanh_toan) == nam) \
        .group_by(TuyenBay.ten_tuyen_bay).all()

    # Tính tổng doanh thu
    tong_doanh_thu = sum([row.doanh_thu for row in doanh_thu_theo_tuyen]) if doanh_thu_theo_tuyen else 0

    # Tính tỷ lệ
    bao_cao = [
        {
            "tuyen_bay": row.ten_tuyen_bay,
            "doanh_thu": row.doanh_thu,
            "so_luot_bay": row.so_luot_bay,
            "ty_le": round((row.doanh_thu / tong_doanh_thu) * 100, 2) if tong_doanh_thu > 0 else 0
        }
        for row in doanh_thu_theo_tuyen
    ]

    # Render template báo cáo doanh thu
    return render_template('baocaodoanhthu.html', bao_cao=bao_cao, tong_doanh_thu=tong_doanh_thu, thang=thang, nam=nam)

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    err_msg = ''
    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']
        if password == confirm:
            anh_dai_dien = ''
            if 'anh_dai_dien' in request.files:
                res = cloudinary.uploader.upload(request.files['anh_dai_dien'])
                anh_dai_dien = res['secure_url']

            try:
                dao.register(name=request.form['name'],
                             username=request.form['username'],
                             password=password, anh_dai_dien=anh_dai_dien)
                return redirect('/login')
            except ValueError as ve:
                err_msg = str(ve)
            except Exception:
                err_msg = 'Hệ thống đang lỗi. Vui lòng thử lại sau !!'
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            n = request.args.get('next')
            return redirect(n if n else '/')
        else:
            err_msg = 'Tên đăng nhập hoặc Mật khẩu không chính xác !!!'
    return render_template('login.html', err_msg=err_msg)


@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect(url_for('login'))


@app.route('/nhapthongtinbaocao', methods=['GET', 'POST'])
def nhapthongtin():
    if request.method == 'POST':
        # Lấy giá trị tháng và năm từ form
        thang = request.form['thang']
        nam = request.form['nam']
        # Chuyển thẳng đến route báo cáo doanh thu và truyền giá trị tháng và năm
        return bao_cao_doanh_thu_theo_thang(thang, nam)
    return render_template('nhapthongtinbaocao.html')






class QuyDinhHeThongForm(FlaskForm):
    so_luong_san_bay = IntegerField('Số lượng sân bay', validators=[DataRequired(), NumberRange(min=1)])
    thoi_gian_bay_toi_thieu = IntegerField('Thời gian bay tối thiểu (phút)', validators=[DataRequired(), NumberRange(min=1)])
    so_san_bay_trung_gian_toi_da = IntegerField('Số sân bay trung gian tối đa', validators=[DataRequired(), NumberRange(min=0)])
    thoi_gian_dung_toi_thieu = IntegerField('Thời gian dừng tối thiểu (phút)', validators=[DataRequired(), NumberRange(min=1)])
    thoi_gian_dung_toi_da = IntegerField('Thời gian dừng tối đa (phút)', validators=[DataRequired(), NumberRange(min=1)])
    thoi_gian_ban_ve = IntegerField('Thời gian bán vé (giờ)', validators=[DataRequired(), NumberRange(min=1)])
    thoi_gian_dat_ve = IntegerField('Thời gian đặt vé (giờ)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Cập nhật')

@app.route('/quydinhhethong', methods=['GET', 'POST'])
@login_required
def thay_doi_quy_dinh():
    # Query the first record of QuyDinhHeThong
    quy_dinh = QuyDinhHeThong.query.first()

    # If not exist, create a new record with default values
    if not quy_dinh:
        quy_dinh = QuyDinhHeThong(
            so_luong_san_bay=10,
            thoi_gian_bay_toi_thieu=30,
            so_san_bay_trung_gian_toi_da=5,
            thoi_gian_dung_toi_thieu=15,
            thoi_gian_dung_toi_da=60,
            thoi_gian_ban_ve=24,
            thoi_gian_dat_ve=12,
        )
        db.session.add(quy_dinh)
        db.session.commit()

    # Initialize the form with the data from the database
    form = QuyDinhHeThongForm(obj=quy_dinh)

    # Handle form submission
    if form.validate_on_submit():
        form.populate_obj(quy_dinh)  # Update the quy_dinh object with form data
        db.session.commit()  # Save changes to the database
        flash('Cập nhật quy định hệ thống thành công!', 'success')
        return redirect(url_for('home'))

    # Render the page to change system regulations
    return render_template('quydinhhethong.html', form=form)



@app.route('/them_tuyen_bay', methods=['GET', 'POST'])
@login_required
def them_tuyen_bay():
    if request.method == 'POST':
        ten_tuyen_bay = request.form.get('ten_tuyen_bay')

        # Kiểm tra nếu tuyến bay đã tồn tại
        tuyen_bay_ton_tai = TuyenBay.query.filter_by(ten_tuyen_bay=ten_tuyen_bay).first()
        if tuyen_bay_ton_tai:
            flash('Tuyến bay đã tồn tại.', 'danger')
            return redirect(url_for('them_tuyen_bay'))

        # Tạo tuyến bay mới
        tuyen_bay_moi = TuyenBay(ten_tuyen_bay=ten_tuyen_bay)
        db.session.add(tuyen_bay_moi)
        db.session.commit()
        flash('Tuyến bay đã được thêm thành công!', 'success')
        return redirect(url_for('danh_sach_tuyen_bay'))

    return render_template('them_tuyen_bay.html')

@app.route('/danh_sach_tuyen_bay')
@login_required
def danh_sach_tuyen_bay():
    tuyen_bays = TuyenBay.query.all()
    return render_template('danh_sach_tuyen_bay.html', tuyen_bays=tuyen_bays)


@app.route('/sua_tuyen_bay/<int:tuyen_bay_id>', methods=['GET', 'POST'])
@login_required
def sua_tuyen_bay(tuyen_bay_id):
    tuyen_bay = TuyenBay.query.get_or_404(tuyen_bay_id)

    if request.method == 'POST':
        ten_tuyen_bay_moi = request.form.get('ten_tuyen_bay')
        tuyen_bay.ten_tuyen_bay = ten_tuyen_bay_moi
        db.session.commit()
        flash('Tuyến bay đã được cập nhật thành công!', 'success')
        return redirect(url_for('danh_sach_tuyen_bay'))

    return render_template('sua_tuyen_bay.html', tuyen_bay=tuyen_bay)



@app.route('/xoa_tuyen_bay/<int:tuyen_bay_id>', methods=['GET', 'POST'])
@login_required
def xoa_tuyen_bay(tuyen_bay_id):
    tuyen_bay = TuyenBay.query.get_or_404(tuyen_bay_id)
    db.session.delete(tuyen_bay)
    db.session.commit()
    flash('Tuyến bay đã được xóa thành công!', 'success')
    return redirect(url_for('danh_sach_tuyen_bay'))


if __name__ == '__main__':
    app.run(port=5002, debug=True)
