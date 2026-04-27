from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, 
                           QTextEdit, QMessageBox, QInputDialog, QHeaderView)
from PyQt5.QtCore import Qt
from password_manager.storage import PasswordStorage

class PasswordManagerApp(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.master_password = None
        self.storage = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализирует интерфейс"""
        self.setWindowTitle('🔐 Password Manager Secure')
        self.setGeometry(100, 100, 1000, 600)
        
        # Запрос главного пароля
        self.ask_master_password()
        
        if self.master_password is None:
            return
        
        # Инициализация хранилища
        self.storage = PasswordStorage()
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        
        # Layout для кнопок
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ Добавить пароль')
        add_btn.clicked.connect(self.add_password_dialog)
        
        edit_btn = QPushButton('✏️ Редактировать')
        edit_btn.clicked.connect(self.edit_password_dialog)
        
        delete_btn = QPushButton('🗑️ Удалить')
        delete_btn.clicked.connect(self.delete_password)
        
        show_btn = QPushButton('👁️ Показать пароль')
        show_btn.clicked.connect(self.show_password)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(show_btn)
        
        # Таблица паролей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Сайт', 'Пользователь', 'Заметки', 'Дата создания'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        
        central_widget.setLayout(main_layout)
        
        # Загружаем пароли
        self.load_passwords_table()
    
    def ask_master_password(self):
        """Запрашивает главный пароль при первом запуске"""
        storage = PasswordStorage()
        
        if not storage.passwords:  # Первый запуск
            password, ok = QInputDialog.getText(
                self, 'Создание главного пароля', 
                'Создайте главный пароль для защиты вашего хранилища:\n(Запомните его!)',
                QLineEdit.Password
            )
            
            if ok and password:
                self.master_password = password
            else:
                self.close()
        else:
            password, ok = QInputDialog.getText(
                self, 'Вход', 
                'Введите главный пароль:',
                QLineEdit.Password
            )
            
            if ok and password:
                # Проверяем пароль
                try:
                    storage.get_all_passwords(password)
                    self.master_password = password
                except:
                    QMessageBox.critical(self, 'Ошибка', 'Неверный главный пароль!')
                    self.close()
            else:
                self.close()
    
    def load_passwords_table(self):
        """Загружает пароли в таблицу"""
        self.table.setRowCount(0)
        
        try:
            passwords = self.storage.get_all_passwords(self.master_password)
            
            for row, pwd in enumerate(passwords):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(pwd['site']))
                self.table.setItem(row, 1, QTableWidgetItem(pwd['username']))
                self.table.setItem(row, 2, QTableWidgetItem(pwd['notes']))
                self.table.setItem(row, 3, QTableWidgetItem(pwd['created_at'][:10]))
                
                # Сохраняем ID в первой ячейке (скрытый)
                self.table.item(row, 0).setData(Qt.UserRole, pwd['id'])
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при загрузке паролей: {str(e)}')
    
    def add_password_dialog(self):
        """Диалог добавления пароля"""
        dialog = QDialog(self)
        dialog.setWindowTitle('Добавить пароль')
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # Поля ввода
        layout.addWidget(QLabel('Сайт:'))
        site_input = QLineEdit()
        layout.addWidget(site_input)
        
        layout.addWidget(QLabel('Пользователь:'))
        user_input = QLineEdit()
        layout.addWidget(user_input)
        
        layout.addWidget(QLabel('Пароль:'))
        pass_input = QLineEdit()
        pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(pass_input)
        
        layout.addWidget(QLabel('Заметки:'))
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(100)
        layout.addWidget(notes_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Сохранить')
        cancel_btn = QPushButton('Отмена')
        
        def save():
            if site_input.text() and user_input.text() and pass_input.text():
                self.storage.add_password(
                    site_input.text(),
                    user_input.text(),
                    pass_input.text(),
                    notes_input.toPlainText(),
                    self.master_password
                )
                QMessageBox.information(self, 'Успех', 'Пароль добавлен!')
                self.load_passwords_table()
                dialog.close()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
        
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def edit_password_dialog(self):
        """Диалог редактирования пароля"""
        if self.table.currentRow() < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пароль для редактирования!')
            return
        
        entry_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        pwd = self.storage.get_password(entry_id, self.master_password)
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Редактировать пароль')
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel('Сайт:'))
        site_input = QLineEdit()
        site_input.setText(pwd['site'])
        layout.addWidget(site_input)
        
        layout.addWidget(QLabel('Пользователь:'))
        user_input = QLineEdit()
        user_input.setText(pwd['username'])
        layout.addWidget(user_input)
        
        layout.addWidget(QLabel('Пароль:'))
        pass_input = QLineEdit()
        pass_input.setText(pwd['password'])
        pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(pass_input)
        
        layout.addWidget(QLabel('Заметки:'))
        notes_input = QTextEdit()
        notes_input.setText(pwd['notes'])
        notes_input.setMaximumHeight(100)
        layout.addWidget(notes_input)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Сохранить')
        cancel_btn = QPushButton('Отмена')
        
        def save():
            self.storage.update_password(
                entry_id,
                site_input.text(),
                user_input.text(),
                pass_input.text(),
                notes_input.toPlainText(),
                self.master_password
            )
            QMessageBox.information(self, 'Успех', 'Пароль обновлен!')
            self.load_passwords_table()
            dialog.close()
        
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def delete_password(self):
        """Удаляет пароль"""
        if self.table.currentRow() < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пароль для удаления!')
            return
        
        reply = QMessageBox.question(self, 'Подтверждение', 
                                     'Вы уверены, что хотите удалить этот пароль?',
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            entry_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
            self.storage.delete_password(entry_id)
            self.load_passwords_table()
            QMessageBox.information(self, 'Успех', 'Пароль удален!')
    
    def show_password(self):
        """Показывает пароль"""
        if self.table.currentRow() < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пароль для просмотра!')
            return
        
        entry_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        pwd = self.storage.get_password(entry_id, self.master_password)
        
        QMessageBox.information(self, f'Пароль для {pwd["site"]}', 
                                f'Пароль: {pwd["password"]}');
