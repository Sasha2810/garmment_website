from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)

# Секретный ключ для сессий
app.secret_key = 'aP9#fN4@8TgL!kE1$2ZxVpRqSdUoWmYq'

# Настройки для загрузки изображений
app.config['UPLOAD_FOLDER'] = 'static/image'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Простой список товаров
products = [
    {"name": "Лонгслив Garment", "description": "Стильный и удобный. Изготовлен из хороших материалов.", "price": 3499, "link": "https://t.me/garmmentclothes", "images": ["Front.png", "Back.png"]}
]

# Архив товаров
archived_products = []

# Функция для проверки расширения файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница
@app.route('/')
def index():
    return render_template('index.html', products=products, archived_products=archived_products)

# Админка с базовой авторизацией
@app.route('/QW1F23V4', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        images = request.files.getlist('images')

        if not name or not description or not price or not images:
            flash('Все поля обязательны для заполнения!', 'danger')
            return redirect(url_for('admin_panel'))

        filenames = []
        for image in images:
            if image and allowed_file(image.filename):
                filename = image.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(file_path)
                filenames.append(filename)
            else:
                flash('Некорректный формат изображения. Поддерживаемые форматы: PNG, JPG, JPEG, GIF.', 'danger')
                return redirect(url_for('admin_panel'))

        new_product = {
            "name": name,
            "description": description,
            "price": int(price),
            "images": filenames
        }
        products.append(new_product)
        flash(f'Товар "{name}" добавлен в каталог!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('admin.html', products=products, archived_products=archived_products)

# Удаление товара из каталога
@app.route('/delete_from_catalog/<int:product_id>', methods=['POST'])
def delete_from_catalog(product_id):
    if 0 <= product_id < len(products):
        deleted_product = products.pop(product_id)
        flash(f'Товар "{deleted_product["name"]}" удален из каталога!', 'success')
    else:
        flash('Товар не найден!', 'danger')
    return redirect(url_for('admin_panel'))

# Удаление товара из архива
@app.route('/delete_from_archive/<int:product_id>', methods=['POST'])
def delete_from_archive(product_id):
    if 0 <= product_id < len(archived_products):
        deleted_product = archived_products.pop(product_id)
        flash(f'Товар "{deleted_product["name"]}" удален из архива!', 'success')
    else:
        flash('Товар не найден!', 'danger')
    return redirect(url_for('admin_panel'))

# Архивирование товара
@app.route('/archive/<int:product_id>', methods=['POST'])
def archive_product(product_id):
    if 0 <= product_id < len(products):
        archived_products.append(products.pop(product_id))
        flash(f'Товар "{archived_products[-1]["name"]}" перемещен в архив!', 'success')
    else:
        flash('Товар не найден!', 'danger')
    return redirect(url_for('admin_panel'))

# Добавление товара в корзину
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []  # Инициализируем корзину, если она еще не существует

    if 0 <= product_id < len(products):
        # Проверяем, есть ли товар уже в корзине по ID
        if any(item['id'] == product_id for item in session['cart']):
            flash('Этот товар уже в корзине!', 'info')
            return redirect(url_for('index'))  # Если товар уже в корзине, ничего не делаем

        # Добавляем товар в корзину
        item = products[product_id].copy()
        item['id'] = product_id  # Добавляем ID товара для проверки
        session['cart'].append(item)
        session.modified = True  # Указываем, что сессия изменена
        flash(f'Товар "{item["name"]}" добавлен в корзину!', 'success')

    return redirect(url_for('index'))

# Удаление товара из корзины
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True  # Указываем, что сессия была изменена
        flash('Товар удален из корзины!', 'success')

    return redirect(url_for('index'))

# Оформление заказа
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста!', 'warning')
        return redirect(url_for('index'))  # Если корзина пуста, перенаправляем на главную страницу

    total = sum(item['price'] for item in session['cart'])  # Суммируем цены товаров из сессии
    return render_template('checkout.html', cart=session['cart'], total=total)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
