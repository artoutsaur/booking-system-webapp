from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Workplace, log_action
from datetime import datetime, date

bp = Blueprint('bookings', __name__)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_booking():
    workplace_id = request.args.get('workplace_id', type=int)
    workplaces = Workplace.query.all()
    
    if request.method == 'POST':
        wp_id = request.form.get('workplace_id')
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')

        # Конвертация строк в объекты даты
        try:
            start_dt = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Некорректный формат даты.', 'danger')
            return redirect(url_for('bookings.new_booking'))

        # Базовые проверки
        if start_dt < date.today():
            flash('Нельзя бронировать на прошедшие даты.', 'warning')
            return redirect(url_for('bookings.new_booking'))
        
        if start_dt > end_dt:
            flash('Дата окончания не может быть раньше даты начала.', 'warning')
            return redirect(url_for('bookings.new_booking'))

        # КЛЮЧЕВАЯ ЛОГИКА: Проверка на пересечение дат
        # Ищем любую существующую бронь, которая пересекается с выбранным интервалом
        conflict = Booking.query.filter(
            Booking.workplace_id == wp_id,
            Booking.end_date >= start_dt,
            Booking.start_date <= end_dt
        ).first()

        if conflict:
            flash(f'Это место уже занято с {conflict.start_date.strftime("%d.%m")} по {conflict.end_date.strftime("%d.%m")}.', 'danger')
        else:
            new_res = Booking(
                user_id=current_user.id,
                workplace_id=wp_id,
                start_date=start_dt,
                end_date=end_dt
            )
            db.session.add(new_res)
            db.session.commit()
            
            wp_name = Workplace.query.get(wp_id).name
            log_action(current_user.id, f"Забронировал место {wp_name} ({start_str} - {end_str})")
            flash('Место успешно забронировано!', 'success')
            return redirect(url_for('bookings.my_bookings'))

    return render_template('bookings/new.html', workplaces=workplaces, selected_wp=workplace_id)

@bp.route('/my')
@login_required
def my_bookings():
    # Получаем бронирования пользователя, сначала самые свежие
    user_res = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_date.desc()).all()
    return render_template('bookings/my_bookings.html', bookings=user_res)

@bp.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    booking = Booking.query.get_or_404(id)
    
    # Проверка прав (отменить может только владелец или админ)
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('У вас нет прав для отмены этой брони.', 'danger')
        return redirect(url_for('bookings.my_bookings'))
    
    wp_name = booking.workplace.name
    log_action(current_user.id, f"Отменил бронь места {wp_name} (ID: {id})")
    
    db.session.delete(booking)
    db.session.commit()
    flash('Бронирование успешно отменено.', 'success')
    return redirect(url_for('bookings.my_bookings'))