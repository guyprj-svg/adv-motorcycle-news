from flask import Flask, render_template
import feedparser
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import threading
import time
import re

app = Flask(__name__)

# אחסון החדשות בזיכרון (במקום מסד נתונים)
NEWS_STORAGE = []
HIMALAYAN_NEWS = []

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
    'off-road', 'touring', 'ktm', 'bmw', 'rally', 'scrambler',
    'transalp', 'multistrada', 'versys', 'v-strom', 'tuareg'
]

HIMALAYAN_KEYWORDS = ['himalayan', 'himalaya', 'royal enfield 450', 'sherpa']


def translate_to_hebrew(text):
    """
    תרגום טקסט לעברית באמצעות שירות תרגום
    """
    if not text or len(text) < 10:
        return text
    
    try:
        # שימוש ב-API חינמי של MyMemory
        # חילוק הטקסט לחלקים (API מוגבל ל-500 תווים)
        max_chunk = 500
        chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
        
        translated_chunks = []
        for chunk in chunks[:20]:  # מקסימום 20 חלקים (10,000 תווים)
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': chunk,
                'langpair': 'en|he'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('responseData', {}).get('translatedText', chunk)
                translated_chunks.append(translated_text)
                time.sleep(0.5)  # המתנה בין בקשות
            else:
                translated_chunks.append(chunk)  # אם נכשל, השאר באנגלית
        
        return '\n\n'.join(translated_chunks)
        
    except Exception as e:
        print(f"⚠️ תרגום נכשל: {e}")
        return text  # אם נכשל, מחזיר את הטקסט המקורי


def extract_full_article(url):
    """
    מושך את התוכן המלא כולו של הכתבה מה-URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # הסרת סקריפטים, סגנונות, ניווט
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
            element.decompose()
        
        article_content = ''
        
        # ניסיון 1: מציאת תג article
        article = soup.find('article')
        
        # ניסיון 2: חיפוש לפי class names נפוצים
        if not article:
            article = soup.find('div', class_=re.compile(
                'article|post-content|entry-content|content-body|story-body|article-body|main-content',
                re.IGNORECASE
            ))
        
        # ניסיון 3: חיפוש לפי ID
        if not article:
            article = soup.find('div', id=re.compile('article|content|post|entry', re.IGNORECASE))
        
        if article:
            # שלב 1: מציאת כל הפסקאות
            paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote'])
            
            # שלב 2: בניית התוכן
            content_parts = []
            for elem in paragraphs:
                text = elem.get_text().strip()
                # סינון פסקאות קצרות מדי (כנראה לא חלק מהתוכן)
                if len(text) > 30:
                    # אם זה כותרת משנה
                    if elem.name in ['h2', 'h3', 'h4']:
                        content_parts.append(f"\n\n### {text}\n")
                    else:
                        content_parts.append(text)
            
            article_content = '\n\n'.join(content_parts)
        
        # אם לא מצאנו דרך article, ניקח את כל הפסקאות מהדף
        if not article_content or len(article_content) < 500:
            all_paragraphs = soup.find_all('p')
            content_parts = []
            for p in all_paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:  # רק פסקאות משמעותיות
                    content_parts.append(text)
            
            article_content = '\n\n'.join(content_parts)
        
        # אם עדיין אין תוכן
        if not article_content:
            return "לא הצלחנו להוריד את התוכן המלא מהמקור. אנא נסה שוב מאוחר יותר."
        
        # ניקוי תווים מיוחדים
        article_content = article_content.replace('\xa0', ' ').replace('\u200b', '')
        
        print(f"  ✅ הורדו {len(article_content)} תווים")
        return article_content
        
    except Exception as e:
        print(f"❌ שגיאה בהורדת כתבה: {e}")
        return f"שגיאה בטעינת התוכן: {str(e)}"


def fetch_and_process_news():
    """
    משיכת חדשות מ-RSS, הורדת תוכן מלא ותרגום
    """
    global NEWS_STORAGE, HIMALAYAN_NEWS
    
    print("🔄 מושך חדשות חדשות מ-RSS feeds...")
    new_articles = []
    himalayan_articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            print(f"📡 מושך מ-{source_name}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # 5 כתבות מכל מקור
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                
                # בדיקה אם זה אדוונצ'ר
                is_adventure = any(kw in title or kw in summary for kw in ADVENTURE_KEYWORDS)
                is_himalayan = any(kw in title or kw in summary for kw in HIMALAYAN_KEYWORDS)
                
                if is_adventure:
                    print(f"  ✅ נמצא: {entry.title}")
                    
                    # הורדת תוכן מלא
                    full_content = extract_full_article(entry.link)
                    
                    # תרגום לעברית!
                    print(f"  🔄 מתרגם לעברית...")
                    title_hebrew = translate_to_hebrew(entry.title)
                    summary_hebrew = translate_to_hebrew(entry.get('summary', '')[:500])
                    content_hebrew = translate_to_hebrew(full_content)
                    
                    # יצירת מאמר
                    article = {
                        'id': len(new_articles) + 1,
                        'title': title_hebrew,
                        'summary': summary_hebrew,
                        'content': content_hebrew,  # תוכן מלא מתורגם!
                        'source': source_name,
                        'source_url': entry.link,
                        'published_date': entry.get('published', 'לאחרונה'),
                        'category': 'himalayan' if is_himalayan else 'adventure',
                        'created_at': datetime.now().isoformat()
                    }
                    
                    new_articles.append(article)
                    
                    if is_himalayan:
                        himalayan_articles.append(article)
                
                time.sleep(0.5)  # המתנה קצרה בין בקשות
                
        except Exception as e:
            print(f"❌ שגיאה ב-{source_name}: {e}")
    
    # עדכון האחסון
    if new_articles:
        NEWS_STORAGE.clear()
        NEWS_STORAGE.extend(new_articles[:12])  # מקסימום 12 כתבות
        print(f"✅ נוספו {len(new_articles)} כתבות!")
    
    if himalayan_articles:
        HIMALAYAN_NEWS.clear()
        HIMALAYAN_NEWS.extend(himalayan_articles[:6])  # מקסימום 6 כתבות הימלאיה
        print(f"✅ נוספו {len(himalayan_articles)} כתבות הימלאיה!")


def load_initial_data():
    """
    טוען נתונים ראשוניים - תוכן מלא בעברית
    """
    global NEWS_STORAGE, HIMALAYAN_NEWS
    
    # כתבות לדוגמה עם תוכן מלא בעברית
    NEWS_STORAGE = [
        {
            'id': 1,
            'title': 'BMW F 900 GS Adventure 2025 - ביקורת מעמיקה',
            'summary': 'ה-F 900 GS Adventure של BMW משלבת את הזריזות של אופנוע בינוני עם יכולות טיולים ארוכים.',
            'content': '''ה-BMW F 900 GS Adventure מייצגת את הגישה הגרמנית המושלמת לאופנועי אדוונצ'ר בקטגוריה הבינונית. עם מנוע טווין 895cc מקורר נוזלים המספק 105 כ"ס ומומנט של 92 נ"מ, האופנוע מציע שילוב מעולה של ביצועים וכלכליות.

מיכל הדלק בנפח 23 ליטר מאפשר טווח נסיעה של כ-500 ק"מ, מה שהופך אותו לאידיאלי לטיולים ארוכים. המתלים של BMW Motorrad מספקים מסלול של 230 מ"מ קדימה ו-215 מ"מ מאחור, מה שמאפשר רכיבת שטח רצינית.

האופנוע מצויד במערכות בטיחות מתקדמות כולל ABS לשטח, בקרת משיכה, ומצבי רכיבה שונים. משקל הנסיעה של 244 ק"ג עם מיכל מלא נשמר סביר למרות הגודל והיכולות.

נקודות חוזק: יציבות מעולה במהירויות כביש, נוחות לנסיעות ארוכות, מתלים איכוtiים, מנוע חזק וכלכלי.

נקודות חולשה: מחיר גבוה יחסית לקטגוריה, משקל מורגש ברכיבת שטח טכנית, גובה מושב של 870 מ"מ עלול להיות מאתגר לרוכבים נמוכים.

סיכום: אופנוע אדוונצ'ר מצוין לרוכבים המחפשים שילוב של יכולות טיולים ארוכים עם אפשרויות שטח טובות, תוך שמירה על נוחות ואיכות בנייה גרמנית.''',
            'source': 'Motorcyclist',
            'source_url': '#',
            'published_date': 'פברואר 2026',
            'category': 'adventure'
        },
        {
            'id': 2,
            'title': 'Royal Enfield Himalayan 450 - מבחן 10,000 מייל',
            'summary': 'אחרי 10,000 מייל של שימוש אינטנסיבי, ההימלאיה 450 מוכיחה את עצמה כאופנוע אמין ומאוזן.',
            'content': '''רויאל אנפילד הימלאיה 450 עברה מבחן שטח קשה של 10,000 מייל, והתוצאות מרשימות. המנוע Sherpa החדש בנפח 452cc מקורר נוזלים מספק 40 כ"ס ו-40 נ"מ מומנט, ביצועים שמתגלים כמדויקים לרכיבת אדוונצ'ר.

המנוע פועל בצורה חלקה וללא רעידות, שינוי משמעותי מהדור הקודם. תיבת ההילוכים בעלת 6 הילוכים עובדת בצורה מדויקת, והמצמד קל ונוח.

צריכת הדלק הממוצעת עמדה על 21 ק"מ לליטר, עם טווח נסיעה של כ-360 ק"מ ממיכל הדלק בנפח 17 ליטר. המתלים של Showa מספקים מסלול של 200 מ"מ ומתמודדים היטב עם שטח משתנה.

משקל הנסיעה של 196 ק"ג (יבש) הופך את האופנוע לזריז ונוח לתמרון. גובה המושב של 825 מ"מ מאפשר למרבית הרוכבים להגיע בנוחות לקרקע.

במהלך המבחן לא נתגלו תקלות מכניות משמעותיות. היו כמה תקלות חשמל קלות בקילומטראז' הנמוך שתוקנו במהירות. הבלם האחורי קיבל ביקורות מעורבות בגלל תחושה מעט מעורפלת.

המחיר ההתחלתי של $5,799 הופך את ההימלאיה 450 לבעלת אחד מיחסי המחיר-ביצועים הטובים בקטגוריה. האופנוע מתאים במיוחד לרוכבים מתחילים בעולם האדוונצ'ר, אך גם מנוסים ימצאו בה ערך רב.

המלצה: בחירה מצוינת לכל מי שמחפש אופנוע אדוונצ'ר אמין, פשוט לתחזוקה, וכלכלי, ללא ויתור על יכולות אמיתיות.''',
            'source': 'Adventure Motorcycle',
            'source_url': '#',
            'published_date': 'ינואר 2026',
            'category': 'himalayan'
        }
    ]
    
    HIMALAYAN_NEWS = [NEWS_STORAGE[1]]  # כתבת ההימלאיה


def update_news_periodically():
    """
    עדכון חדשות אוטומטי כל 24 שעות
    """
    while True:
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} - מתחיל עדכון...")
        fetch_and_process_news()
        print(f"✅ עדכון הושלם. השרת ימשיך לרוץ...")
        # המתנה של 24 שעות
        time.sleep(24 * 60 * 60)


@app.route('/')
def index():
    """עמוד הבית עם כל החדשות"""
    return render_template('index.html', articles=NEWS_STORAGE)


@app.route('/article/<int:article_id>')
def article(article_id):
    """עמוד כתבה בודדת - תוכן מלא בעברית!"""
    article = next((item for item in NEWS_STORAGE if item['id'] == article_id), None)
    
    if article is None:
        # אם לא נמצא, חזרה לעמוד הבית
        return render_template('index.html', articles=NEWS_STORAGE)
    
    return render_template('article.html', article=article)


@app.route('/himalayan')
def himalayan():
    """עמוד הימלאיה 450 עם כתבות מעודכנות"""
    return render_template('himalayan.html', himalayan_articles=HIMALAYAN_NEWS)


@app.route('/update-now')
def update_now():
    """עדכון ידני של חדשות"""
    threading.Thread(target=fetch_and_process_news, daemon=True).start()
    return '''
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; text-align: center; padding: 100px; }
            h1 { color: #ff8533; }
        </style>
    </head>
    <body>
        <h1>🔄 מעדכן חדשות...</h1>
        <p>זה עלול לקחת מספר דקות. החדשות יתעדכנו ברקע.</p>
        <p><a href="/">חזרה לעמוד הבית</a></p>
        <script>setTimeout(() => window.location.href = '/', 10000);</script>
    </body>
    </html>
    '''


if __name__ == '__main__':
    print("🚀 מתחיל את השרת...")
    
    # טעינת נתונים ראשוניים
    load_initial_data()
    
    # ניסיון למשוך חדשות אמיתיות ברקע
    update_thread = threading.Thread(target=update_news_periodically, daemon=True)
    update_thread.start()
    
    # הפעלת השרת
    port = int(os.environ.get('PORT', 5000))
    print(f"✅ השרת פועל על פורט {port}")
    print("📰 החדשות יתעדכנו אוטומטית כל 24 שעות")
    app.run(debug=False, host='0.0.0.0', port=port)
