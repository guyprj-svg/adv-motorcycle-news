"""
Flask Web Application - Adventure Motorcycle News
אתר דינמי מלא לחדשות אופנועי אדוונצ'ר
"""

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
import feedparser
import os
from threading import Thread
import time
import schedule

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# נתיב למסד הנתונים
DATABASE = 'news.db'

# RSS Feeds
RSS_FEEDS = {
    'Adventure Motorcycle': 'https://adventuremotorcycle.com/feed',
    'Motorcyclist': 'https://www.motorcyclistonline.com/rss/',
    'RideApart': 'https://www.rideapart.com/rss/',
    'Cycle World': 'https://www.cycleworld.com/rss/',
}

ADVENTURE_KEYWORDS = [
    'adventure', 'adv', 'dual-sport', 'gs', 'africa twin',
    'himalayan', 'tenere', 'tiger', 'super adventure',
    'off-road', 'touring', 'ktm', 'bmw gs', 'scrambler'
]


def init_db():
    """יצירת מסד נתונים"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            source TEXT,
            source_url TEXT,
            published_date TEXT,
            category TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def get_db_connection():
    """חיבור למסד נתונים"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_and_save_news():
    """משיכה ושמירה של חדשות"""
    print("🔄 מושך חדשות חדשות...")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:
                title = entry.title.lower()
                summary = entry.get('summary', '').lower()
                
                # בדיקה אם זה קשור לאדוונצ'ר
                is_adventure = any(kw in title or kw in summary 
                                 for kw in ADVENTURE_KEYWORDS)
                
                if is_adventure:
                    # בדיקה אם הכתבה כבר קיימת
                    c.execute('SELECT id FROM articles WHERE source_url = ?',
                             (entry.link,))
                    
                    if not c.fetchone():
                        # הוספת כתבה חדשה
                        c.execute('''
                            INSERT INTO articles 
                            (title, summary, source, source_url, published_date, category)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            entry.title,
                            entry.get('summary', '')[:500],
                            source_name,
                            entry.link,
                            entry.get('published', ''),
                            'adventure'
                        ))
                        
                        print(f"✅ נוספה: {entry.title}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ שגיאה ב-{source_name}: {e}")
    
    conn.commit()
    conn.close()
    print("✅ עדכון הושלם!")


def schedule_updates():
    """תזמון עדכונים אוטומטיים"""
    schedule.every().day.at("08:00").do(fetch_and_save_news)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


# Routes
@app.route('/')
def index():
    """עמוד הבית"""
    conn = get_db_connection()
    articles = conn.execute(
        'SELECT * FROM articles ORDER BY created_at DESC LIMIT 12'
    ).fetchall()
    conn.close()
    
    return render_template('index.html', articles=articles)


@app.route('/article/<int:article_id>')
def article(article_id):
    """עמוד כתבה בודדת"""
    conn = get_db_connection()
    article = conn.execute(
        'SELECT * FROM articles WHERE id = ?', (article_id,)
    ).fetchone()
    conn.close()
    
    if article is None:
        return redirect(url_for('index'))
    
    return render_template('article.html', article=article)


@app.route('/himalayan')
def himalayan():
    """עמוד הימלאיה 450"""
    return render_template('himalayan.html')


@app.route('/update-now')
def update_now():
    """עדכון ידני של חדשות"""
    fetch_and_save_news()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # יצירת מסד נתונים
    init_db()
    
    # עדכון ראשוני
    fetch_and_save_news()
    
    # הפעלת תזמון ברקע
    update_thread = Thread(target=schedule_updates, daemon=True)
    update_thread.start()
    
    # הפעלת השרת
    print("🚀 השרת פועל על http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
