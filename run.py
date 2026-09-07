# -*- coding: utf-8 -*-
from flask import Flask
# ... остальной код без изменений ...
from app import create_app, db
from app.models import User, Workplace, Booking, Log

# Создаем экземпляр приложения
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Workplace': Workplace, 
        'Booking': Booking, 
        'Log': Log
    }

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)