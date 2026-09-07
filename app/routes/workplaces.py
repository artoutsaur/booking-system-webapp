from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Workplace, Booking, log_action
from app.utils.decorators import admin_required

bp = Blueprint('workplaces', __name__)

# Маршрут для просмотра всех мест (доступно всем авторизованным)
@bp.route('/')
@login_required
def list_workplaces():
    workplaces = Workplace.query.order_by(Workplace.name).all()
    return render_template('workplaces/list.html', workplaces=workplaces)

# Маршрут для управления местами (только для админов)
@bp.route('/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def manage():
    if request.method == 'POST':
        # Логика добавления нового места
        name = request.form.get('name')
        if name:
            new_wp = Workplace(name=name)
            db.session.add(new_wp)
            db.session.commit()
            log_action(current_user.id, f"Добавлено рабочее место: {name}")
            flash(f'Рабочее место "{name}" успешно добавлено!', 'success')
        return redirect(url_for('workplaces.manage'))

    workplaces = Workplace.query.order_by(Workplace.name).all()
    return render_template('workplaces/manage.html', workplaces=workplaces)

# Маршрут удаления
@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    workplace = Workplace.query.get_or_404(id)
    force = request.form.get('force') == 'true'
    
    # Проверяем наличие бронирований
    has_bookings = workplace.bookings.count() > 0
    
    if has_bookings and not force:
        flash(f'Нельзя удалить "{workplace.name}", так как на него есть бронирования. Используйте принудительное удаление.', 'warning')
        return redirect(url_for('workplaces.manage'))
    
    action_type = "Принудительное удаление" if force else "Удаление"
    log_action(current_user.id, f"{action_type} места: {workplace.name} (ID: {id})")
    
    db.session.delete(workplace)
    db.session.commit()
    
    flash(f'Рабочее место "{workplace.name}" удалено.', 'success')
    return redirect(url_for('workplaces.manage'))