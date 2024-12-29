from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os

app = Flask(__name__)

secret_key = os.urandom(24)  
app.secret_key = secret_key.hex()  

app.config['UPLOAD_FOLDER'] = 'static/image'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Простой список товаров
products = [
    {"name": "Лонгслив Garment", "description": "Стильный и удобный. Изготовлен из хороших материалов.", "price": 3499, "link": "https://t.me/garmmentclothes", "images": ["Front.png", "Back.png"]}
]

archived_products = []

# Главная страница
@app.route('/')
def index():
    for img in products[0]['images']:
        print(url_for('static', filename='image/' + img))

    return render_template('index.html', products=products, archived_products=archived_products)
# Админка
@app.route('/QW1F23V4', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        images = request.files.getlist('images')

        filenames = []
        for image in images:
            if image and image.filename:
                filename = image.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(file_path)
                filenames.append(filename)

        products.append({"name": name, "description": description, "price": int(price), "images": filenames})
        print(products)
        return redirect(url_for('admin_panel'))

    return render_template('admin.html', products=products,  archived_products=archived_products,)

@app.route('/delete_from_catalog/<int:product_id>', methods=['POST'])
def delete_from_catalog(product_id):
    if 0 <= product_id < len(products):
        products.pop(product_id)
    return redirect(url_for('admin_panel'))

@app.route('/delete_from_archive/<int:product_id>', methods=['POST'])
def delete_from_archive(product_id):
    if 0 <= product_id < len(archived_products):
        archived_products.pop(product_id)
    return redirect(url_for('admin_panel'))


@app.route('/archive/<int:product_id>', methods=['POST'])
def archive_product(product_id):
    if 0 <= product_id < len(products):
        print(products)
        archived_products.append(products.pop(product_id))
        print(archived_products)
    return redirect(url_for('admin_panel'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []  # Инициализируем корзину, если она еще не существует

    if 0 <= product_id < len(products):
        # Проверяем, есть ли товар уже в корзине по ID
        if any(item['id'] == product_id for item in session['cart']):
            print("Товар уже в корзине.")
            return redirect(url_for('index'))  # Если товар уже в корзине, ничего не делаем

        # Добавляем товар в корзину
        item = products[product_id].copy()
        item['id'] = product_id  # Добавляем ID товара для проверки
        session['cart'].append(item)
        session.modified = True  # Указываем, что сессия изменена
        print(session['cart'])  # Для отладки

    return redirect(url_for('index'))


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        print("Cart before removal:", session['cart'])  # Для отладки
        # Удаляем элемент по product_id
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True  # Указываем, что сессия была изменена
        print("Cart after removal:", session['cart'])  # Для отладки
    return redirect(url_for('index'))



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('index'))  # Если корзина пуста, перенаправляем на главную страницу

    total = sum(item['price'] for item in session['cart'])  # Суммируем цены товаров из сессии
    print(total)
    
    return render_template('checkout.html', cart=session['cart'], total=total)


    


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)