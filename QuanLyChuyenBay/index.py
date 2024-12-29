
from QuanLyChuyenBay import login, utils, db
from flask import render_template, request, redirect, session, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template
import cloudinary.uploader
from QuanLyChuyenBay import app, dao, models
from QuanLyChuyenBay.dao import load_chuyen_bay, load_san_bay, load_chuyen_bay_theo_tinh_trang, load_hang_ghe_theo_id
from QuanLyChuyenBay.models import ChuyenBay, DatVe, HangGheChuyenBay,SanBay,SanBayTrungGian,TuyenBay,HoaDon,QuyDinhHeThong,User,HangGhe
from flask import render_template, request

from datetime import datetime, timedelta

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route('/', methods=['GET', 'POST'])
def home():
    san_bay_id = request.args.get("san_bay")
    ngay_bay = request.args.get("ngay_bay")

    # Chuyển hướng đến trang chuyenbaylistactive với các tham số tìm kiếm
    if san_bay_id or ngay_bay:
        return redirect(url_for('chuyenbaylistactive', san_bay=san_bay_id, ngay_bay=ngay_bay))

    sanbays = load_san_bay()

    return render_template('index.html', san_bay=san_bay_id, ngay_bay=ngay_bay, sanbays=sanbays)



from datetime import datetime

@app.route('/chuyenbaylist')
def chuyenbaylistactive():
    san_bay_id = request.args.get("san_bay")
    ngay_bay = request.args.get("ngay_bay")

    chuyen_bay_list = load_chuyen_bay()  # Hàm này nên lấy đầy đủ dữ liệu từ database

    if san_bay_id:
        try:
            chuyen_bay_list = [
                cb for cb in chuyen_bay_list
                if int(san_bay_id) in [sbtg.san_bay_id for sbtg in cb.chuyen_bay_san_bay_trung_gians]
            ]
        except AttributeError:
            # Lỗi có thể xảy ra khi danh sách trung gian rỗng
            pass

    if ngay_bay:
        try:
            ngay_bay_date = datetime.strptime(ngay_bay, '%Y-%m-%d').date()
            chuyen_bay_list = [cb for cb in chuyen_bay_list if cb.ngay_bay.date() == ngay_bay_date]
        except ValueError:
            # Handle invalid date format
            pass

    chuyen_bay_list_active = [cb for cb in chuyen_bay_list if cb.tinh_trang]

    return render_template('chuyenbaylist.html', chuyen_bay_active=chuyen_bay_list_active)




@app.route('/order/<int:chuyen_bay_id>', methods=['GET', 'POST'])
@login_required
def order(chuyen_bay_id):
    chuyen_bay = ChuyenBay.query.get_or_404(chuyen_bay_id)
    hang_ghe_chuyen_bay = HangGheChuyenBay.query.filter_by(chuyen_bay_id=chuyen_bay_id).all()

    # Lấy quy định hệ thống
    quy_dinh = QuyDinhHeThong.query.first()  # Lấy quy định hệ thống đầu tiên

    # Lấy thời gian hiện tại
    now = datetime.now()

    # Chuyển đổi thoiGianDatVe sang giá trị số nguyên
    thoi_gian_dat_ve = int(quy_dinh.thoiGianDatVe)  # Chuyển đổi giá trị từ quy định hệ thống

    # Kiểm tra nếu thời gian hiện tại nằm trong khoảng 4 giờ cuối cùng của thời gian bay
    if now > chuyen_bay.ngay_bay - timedelta(hours=thoi_gian_dat_ve):
        flash('Bạn chỉ được phép mua vé trước ít nhất {} tiếng so với thời gian bay.'.format(thoi_gian_dat_ve), 'danger')
        return redirect(url_for('chuyenbaylistactive'))

    if request.method == 'POST':
        ten_hanh_khach = request.form.get('ten_hanh_khach')
        cccd = request.form.get('cccd')
        sdt = request.form.get('sdt')
        hang_ve_id = request.form.get('hang_ve')

        # Kiểm tra điều kiện vé
        hang_ve = HangGheChuyenBay.query.get(hang_ve_id)
        if not hang_ve or hang_ve.so_luong_ghe <= 0:
            flash('Hạng ghế không còn chỗ!', 'danger')
            return redirect(url_for('order', chuyen_bay_id=chuyen_bay_id))

        # Cập nhật số lượng vé
        hang_ve.so_luong_ghe -= 1

        # Lưu thông tin đặt vé
        dat_ve = DatVe(
            user_id=current_user.id,
            ten_hanh_khach=ten_hanh_khach,
            cccd=cccd,
            sdt=sdt,
            chuyen_bay_id=chuyen_bay.id,
            hang_ghe_chuyen_bay_id=hang_ve.id
        )
        db.session.add(dat_ve)
        db.session.commit()

        flash('Đặt vé thành công!', 'success')
        return redirect(url_for('thanhtoan', chuyen_bay_id=chuyen_bay.id, hang_ve_id=hang_ve.id))

    return render_template('order.html', chuyen_bay=chuyen_bay, hang_ghe_chuyen_bay=hang_ghe_chuyen_bay)


@app.route('/tao_chuyen_bay', methods=['GET', 'POST'])
@login_required
def tao_chuyen_bay():
    if request.method == 'POST':
        # Lấy thông tin từ form
        ten_chuyen_bay = request.form.get('ten_chuyen_bay')
        tuyen_bay_id = request.form.get('tuyen_bay_id')
        ngay_bay = request.form.get('ngay_bay')
        tinh_trang = request.form.get('tinh_trang') == 'on'
        so_luong_ghe_hang_1 = int(request.form.get('so_luong_ghe_hang_1'))
        so_luong_ghe_hang_2 = int(request.form.get('so_luong_ghe_hang_2'))

        # Tạo chuyến bay mới
        chuyen_bay = ChuyenBay(
            ten_chuyen_bay=ten_chuyen_bay,
            tuyen_bay_id=int(tuyen_bay_id),
            ngay_bay=datetime.strptime(ngay_bay, '%Y-%m-%dT%H:%M'),
            tinh_trang=tinh_trang
        )
        db.session.add(chuyen_bay)
        db.session.commit()

        # Tạo hạng ghế cho chuyến bay
        hang_ghe_1 = HangGheChuyenBay(
            hang_ghe_id=1,  # ID của hạng ghế 1
            chuyen_bay_id=chuyen_bay.id,
            so_luong_ghe=so_luong_ghe_hang_1
        )
        hang_ghe_2 = HangGheChuyenBay(
            hang_ghe_id=2,  # ID của hạng ghế 2
            chuyen_bay_id=chuyen_bay.id,
            so_luong_ghe=so_luong_ghe_hang_2
        )
        db.session.add_all([hang_ghe_1, hang_ghe_2])

        # Lưu các sân bay trung gian
        san_bay_trung_gians = request.form.getlist('san_bay_trung_gian')
        thoi_gian_dungs = request.form.getlist('thoi_gian_dung')
        ghi_chus = request.form.getlist('ghi_chu')

        for i in range(len(san_bay_trung_gians)):
            san_bay_trung_gian = SanBayTrungGian(
                chuyen_bay_id=chuyen_bay.id,
                san_bay_id=int(san_bay_trung_gians[i]),
                thoi_gian_dung=int(thoi_gian_dungs[i]),
                ghi_chu=ghi_chus[i]
            )
            db.session.add(san_bay_trung_gian)

        db.session.commit()
        flash('Tạo chuyến bay thành công!', 'success')
        return redirect(url_for('home'))

    # Lấy danh sách tuyến bay và sân bay từ cơ sở dữ liệu
    tuyen_bays = TuyenBay.query.all()
    san_bays = SanBay.query.all()

    return render_template('tao_chuyen_bay.html', tuyen_bays=tuyen_bays, san_bays=san_bays)


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













if __name__ == '__main__':
    app.run(port=5002,debug=True)
