from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Booking, Workplace, Log, log_action
from app.utils.decorators import admin_required, super_admin_required
from sqlalchemy import func

bp = Blueprint('admin', __name__)

@bp.route('/stats')
@login_required
@admin_required
def statistics():
    # Собираем данные для карточек
    stats = {
        'users_count': User.query.count(),
        'bookings_count': Booking.query.count(),
        'workplaces_count': Workplace.query.count(),
    }
    
    # Топ-5 самых популярных мест (на основе кол-ва бронирований)
    popular_workplaces = db.session.query(
        Workplace.name, func.count(Booking.id).label('total')
    ).join(Booking).group_by(Workplace.id).order_by(func.count(Booking.id).desc()).limit(5).all()

    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()

    all_bookings = Booking.query.options(
        db.joinedload(Booking.user),
        db.joinedload(Booking.workplace)
    ).order_by(Booking.created_at.desc()).limit(50).all()

    return render_template('admin/stats.html', 
                           stats=stats, 
                           popular=popular_workplaces, 
                           recent=recent_bookings,   # теперь переменная определена
                           all_bookings=all_bookings)

@bp.route('/logs')
@login_required
@admin_required
def logs():
    # Получаем последние 50 записей логов
    all_logs = Log.query.order_by(Log.created_at.desc()).limit(50).all()
    return render_template('admin/logs.html', logs=all_logs)

@bp.route('/users')
@login_required
@super_admin_required
def manage_users():
    # Управление правами (только для Супер-админа)
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@super_admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_super_admin:
        flash('Нельзя изменить права супер-администратора.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        log_action(current_user.id, f"Изменил права админа для пользователя {user.username} на {user.is_admin}")
        flash(f'Статус админа для {user.username} изменен.', 'success')
    return redirect(url_for('admin.manage_users'))