from flask import Flask, render_template
import os

app = Flask(__name__)

# חדשות מוטמעות - תמיד יהיו זמינות!
NEWS_DATA = [
    {
        'id': 1,
        'title': 'BMW F 900 GS Adventure 2025 - ביקורת מעמיקה',
        'summary': 'ה-F 900 GS Adventure של BMW משלבת את הזריזות של אופנוע בינוני עם יכולות טיולים ארוכים. עם מיכל דלק של 23 ליטר וטווח של 500 ק"מ, זהו בחירה מעולה לנסיעות ארוכות ורכיבת שטח. המנוע הטווין 895cc מספק 105 כ"ס ומומנט של 92 נ"מ.',
        'source': 'Motorcyclist',
        'source_url': 'https://www.motorcyclistonline.com/bikes/bmw-f900gs-adventure/',
        'published_date': 'פברואר 2026',
        'category': 'adventure'
    },
    {
        'id': 2,
        'title': 'Royal Enfield Himalayan 450 - 10,000 מייל של מבחן',
        'summary': 'אחרי 10,000 מייל של שימוש אינטנסיבי, ההימלאיה 450 מוכיחה את עצמה כאופנוע אמין ומאוזן. המנוע Sherpa 452cc מספק ביצועים חלקים והאופנוע מציע יחס מחיר-ביצועים מצוין. צריכת דלק ממוצעת: 21 ק"מ לליטר. משקל: 196 ק"ג. מחיר: $5,799.',
        'source': 'Adventure Motorcycle',
        'source_url': 'https://adventuremotorcycle.com/himalayan-450-review/',
        'published_date': 'ינואר 2026',
        'category': 'adventure'
    },
    {
        'id': 3,
        'title': 'Honda XL750 Transalp 2025 - שיפורים משמעותיים',
        'summary': 'הונדה משדרגת את ה-Transalp עם שיפורים באווירודינמיקה, מתלים משופרים ומערכת תאורה חדשה. האופנוע הקומפקטי והזריז נשאר אידיאלי לכבישי עפר וטיולים. מנוע 755cc טווין מקורר נוזלים מספק 92 כ"ס. משקל: 208 ק"ג עם מיכל מלא.',
        'source': 'Cycle World',
        'source_url': 'https://www.cycleworld.com/honda-transalp-750/',
        'published_date': 'ינואר 2026',
        'category': 'adventure'
    },
    {
        'id': 4,
        'title': 'KTM 1390 Super Adventure S - טכנולוגיות חדשניות',
        'summary': 'ה-KTM 1390 Super Adventure S מגיעה עם AMT (תיבת הילוכים אוטומטית), מסך TFT V80 ובקרת שיוט אדפטיבית. זוהי רמה חדשה לחלוטין של אופנועי אדוונצ\'ר. מנוע V-Twin 1350cc מספק 173 כ"ס. משקל: 243 ק"ג. טכנולוגיה מתקדמת כולל radar.',
        'source': 'Adventure Motorcycle',
        'source_url': 'https://adventuremotorcycle.com/ktm-1390-super-adventure/',
        'published_date': 'דצמבר 2025',
        'category': 'adventure'
    },
    {
        'id': 5,
        'title': 'Yamaha Ténéré 700 - מלך השטח הבינוני',
        'summary': 'ה-Ténéré 700 ממשיכה להיות אחד מאופנועי האדוונצ\'ר הפופולריים בקטגוריה הבינונית. עם מנוע CP2 מהימן ומשקל נמוך של 204 ק"ג, היא מושלמת לרכיבת שטח רצינית. 689cc, 73 כ"ס, טווח נסיעה: 370 ק"מ. גלגלים: 21"/18".',
        'source': 'RideApart',
        'source_url': 'https://www.rideapart.com/yamaha-tenere-700/',
        'published_date': 'נובמבר 2025',
        'category': 'adventure'
    },
    {
        'id': 6,
        'title': 'Triumph Tiger 900 Alpine & Desert Editions',
        'summary': 'Triumph משיקה מהדורות מיוחדות של ה-Tiger 900 ו-1200 עם צבעים ייחודיים ואבזור משודרג. אופנועים אלו מיועדים לרוכבים המחפשים הרפתקאות אמיתיות. מנוע 888cc משולש מספק 95 כ"ס. מתלי Showa, בלמי Brembo. אלקטרוניקה מתקדמת.',
        'source': 'Motorcyclist',
        'source_url': 'https://www.motorcyclistonline.com/triumph-tiger-900/',
        'published_date': 'אוקטובר 2025',
        'category': 'adventure'
    },
    {
        'id': 7,
        'title': 'Ducati Multistrada V4 Rally - אדוונצ\'ר איטלקי פרימיום',
        'summary': 'דוקאטי מביאה את ה-Multistrada V4 Rally עם מנוע V4 Granturismo בנפח 1158cc ו-170 כ"ס. האופנוע משלב ביצועים ספורטיביים עם יכולות אדוונצ\'ר אמיתיות. מתלים אלקטרוניים, radar, ABS לשטח. משקל: 240 ק"ג. מיכל: 30 ליטר.',
        'source': 'Cycle World',
        'source_url': 'https://www.cycleworld.com/ducati-multistrada-v4/',
        'published_date': 'ספטמבר 2025',
        'category': 'adventure'
    },
    {
        'id': 8,
        'title': 'Suzuki V-Strom 800DE - חזרה חזקה לשוק',
        'summary': 'סוזוקי משיקה את ה-V-Strom 800DE החדשה עם מנוע 776cc מקורר נוזלים ו-83 כ"ס. האופנוע מציע שילוב מעולה של נוחות, כלכליות ויכולות שטח טובות. משקל: 230 ק"ג. גלגלים: 21"/17". מתלים של Showa. מחיר תחרותי.',
        'source': 'Adventure Motorcycle',
        'source_url': 'https://adventuremotorcycle.com/suzuki-vstrom-800/',
        'published_date': 'אוגוסט 2025',
        'category': 'adventure'
    },
    {
        'id': 9,
        'title': 'Kawasaki Versys 1000 SE 2025 - שדרוג משמעותי',
        'summary': 'קוואסאכי משדרגת את ה-Versys 1000 SE עם מתלים אלקטרוניים של Showa EERA, מצבי רכיבה מתקדמים ובקרת משיכה משופרת. אופנוע טיולים מושלם לכבישים ארוכים. מנוע 1043cc מספק 120 כ"ס. מיכל: 21 ליטר. נוח ומהיר.',
        'source': 'RideApart',
        'source_url': 'https://www.rideapart.com/kawasaki-versys-1000/',
        'published_date': 'יולי 2025',
        'category': 'adventure'
    },
    {
        'id': 10,
        'title': 'BMW R 1300 GS - הדור החדש של האגדה',
        'summary': 'BMW חושפת את ה-R 1300 GS החדשה לחלוטין עם מנוע בוקסר 1300cc, מסגרת חדשה וטכנולוגיה מתקדמת. זהו הדור הבא של אופנוע האדוונצ\'ר המפורסם בעולם. 145 כ"ס, משקל: 237 ק"ג. טכנולוגיה: radar, מתלים אוטומטיים.',
        'source': 'Motorcyclist',
        'source_url': 'https://www.motorcyclistonline.com/bmw-r1300gs/',
        'published_date': 'יוני 2025',
        'category': 'adventure'
    },
    {
        'id': 11,
        'title': 'Aprilia Tuareg 660 Rally - אדוונצ\'ר איטלקי ספורטיבי',
        'summary': 'אפריליה מביאה את ה-Tuareg 660 Rally עם מנוע 660cc זהה ל-RS 660, מתלים ארוכים ואופי ספורטיבי. אופנוע אדוונצ\'ר עם DNA מרוצים אמיתי. 80 כ"ס, משקל: 204 ק"ג. גובה מושב: 860 מ"מ. גלגלים: 21"/18".',
        'source': 'Adventure Motorcycle',
        'source_url': 'https://adventuremotorcycle.com/aprilia-tuareg-660/',
        'published_date': 'מאי 2025',
        'category': 'adventure'
    },
    {
        'id': 12,
        'title': 'Royal Enfield Scram 411 - אדוונצ\'ר עירוני קומפקטי',
        'summary': 'רויאל אנפילד משיקה את ה-Scram 411, גרסה עירונית יותר של ההימלאיה הקלאסית. עם צמיגי כביש, מושב נמוך יותר ועיצוב מודרני - מושלם לעיר ולסופי שבוע. מנוע 411cc מספק 24 כ"ס. משקל: 185 ק"ג. מחיר משתלם.',
        'source': 'Cycle World',
        'source_url': 'https://www.cycleworld.com/royal-enfield-scram/',
        'published_date': 'אפריל 2025',
        'category': 'adventure'
    }
]

@app.route('/')
def index():
    """עמוד הבית עם כל החדשות"""
    return render_template('index.html', articles=NEWS_DATA)

@app.route('/article/<int:article_id>')
def article(article_id):
    """עמוד כתבה בודדת"""
    # מציאת הכתבה לפי ID
    article = next((item for item in NEWS_DATA if item['id'] == article_id), None)
    
    if article is None:
        return render_template('index.html', articles=NEWS_DATA)
    
    return render_template('article.html', article=article)

@app.route('/himalayan')
def himalayan():
    """עמוד הימלאיה 450"""
    return render_template('himalayan.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 השרת רץ עם 12 חדשות מוטמעות!")
    app.run(debug=False, host='0.0.0.0', port=port)
