# app/auth.py - ПОЛНОСТЬЮ ОБНОВЛЕННЫЙ ФАЙЛ
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        # УДАЛЕНО: email = request.form.get('email')
        password = request.form.get('password')
        
        # Проверка на существующего пользователя
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Создание нового пользователя (без email)
        user = User(username=username)
        user.set_password(password)
        
        # Первый пользователь становится супер-админом
        if User.query.count() == 0:
            user.is_super_admin = True
            user.is_admin = True
            flash('Вы зарегистрированы как супер-администратор!', 'success')
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # ИЗМЕНЕНО: теперь login_identifier вместо email
        login_identifier = request.form.get('login_identifier')  # Поле теперь называется login_identifier
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        # Поиск пользователя по username
        user = User.query.filter_by(username=login_identifier).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))