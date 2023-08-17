import telebot
from telebot import types
import sqlite3
import os
from dotenv import load_dotenv

# خوندن توکن از فایل .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)
# ۱. ساخت دیتابیس با قابلیت عکس و ۱۰ محصول
def setup_db():
    conn = sqlite3.connect('shop_demo.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                      (id INTEGER PRIMARY KEY, name TEXT, price TEXT, stock TEXT, image_url TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            (1, 'یخچال فریزر ال‌جی مدل 2026', '۴۵,۰۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=500&q=80'),
            (2, 'ماشین لباسشویی سامسونگ ۸ کیلویی', '۲۸,۵۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?w=500&q=80'),
            (3, 'مایکروویو سامسونگ مدل جدید', '۱۲,۰۰۰,۰۰۰ تومان', 'ناموجود (به‌زودی)', 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=500&q=80'),
            (4, 'ماشین ظرفشویی بوش ۱۴ نفره', '۳۸,۰۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&q=80'),
            (5, 'تلویزیون هوشمند ایکس‌ویژن ۵۵ اینچ', '۳۲,۰۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500&q=80'),
            (6, 'جاروبرقی شارژی ال‌جی', '۸,۵۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500&q=80'),
            (7, 'یخچال ساید بای ساید سامسونگ', '۶۵,۰۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=500&q=80'),
            (8, 'ماشین لباسشویی اسنوا ۷ کیلویی', '۱۹,۰۰۰,۰۰۰ تومان', 'ناموجود', 'https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?w=500&q=80'),
            (9, 'چای‌ساز و کتری برقی بوش', '۳,۲۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1594213114663-d94db9b17125?w=500&q=80'),
            (10, 'اجاق گاز ۵ شعله مادیران', '۲۲,۰۰۰,۰۰۰ تومان', 'موجود در انبار', 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80')
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
        conn.commit()
    conn.close()

# ۲. پیام استارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🛒 مشاهده محصولات')
    btn2 = types.KeyboardButton('📞 تماس با فروشگاه')
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
                     f"سلام {message.from_user.first_name} عزیز! 🌹\n"
                     "به ربات فروشگاه لوازم خانگی خوش آمدید.\n"
                     "برای دیدن لیست محصولات و قیمت‌ها، روی دکمه زیر بزنید.", 
                     reply_markup=markup)

# ۳. نمایش لیست محصولات
@bot.message_handler(func=lambda message: message.text == '🛒 مشاهده محصولات')
def show_products(message):
    conn = sqlite3.connect('shop_demo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    for prod_id, prod_name in products:
        markup.add(types.InlineKeyboardButton(text=prod_name, callback_data=f"prod_{prod_id}"))
    
    bot.send_message(message.chat.id, "لیست محصولات ما:\nروی هر محصول کلیک کنید تا جزئیات و عکسش رو ببینید 👇", reply_markup=markup)

# ۴. نمایش جزئیات + عکس
@bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
def show_product_details(call):
    prod_id = call.data.split('_')[1]
    
    conn = sqlite3.connect('shop_demo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, stock, image_url FROM products WHERE id = ?", (prod_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        name, price, stock, img_url = product
        text = f"📦 **{name}**\n\n💰 قیمت: {price}\n📊 وضعیت: {stock}"
        bot.answer_callback_query(call.id) 
        
        if img_url:
            bot.send_photo(call.message.chat.id, img_url, caption=text, parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

# ۵. دکمه تماس
@bot.message_handler(func=lambda message: message.text == '📞 تماس با فروشگاه')
def contact(message):
    bot.send_message(message.chat.id, "📞 برای مشاوره و خرید حضوری:\nآدرس: اردبیل، خیابان...\nتلفن: ۰۹۱۴xxxxxxx\n\nمنتظر حضور گرم شما هستیم.")

if __name__ == '__main__':
    setup_db()
    print("ربات روشن شد...")
    bot.infinity_polling()