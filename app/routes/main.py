from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Booking, Workplace, User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Если пользователь уже залогинен, сразу кидаем его в дашборд
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Собираем краткую статистику для отображения в кабинете
    # (аналогично тому, что видел админ в боте)
    stats = {}
    if current_user.is_admin:
        stats = {
            'total_bookings': Booking.query.count(),
            'total_users': User.query.count(),
            'total_workplaces': Workplace.query.count()
        }
    
    # Получаем последние 3 бронирования пользователя для виджета
    my_last_bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.start_date.desc()).limit(3).all()

    return render_template('dashboard.html', stats=stats, last_bookings=my_last_bookings)