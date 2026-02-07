# 🏍️ אתר מגמות בעולם האדוונצ'ר - אתר דינמי אמיתי!

## ✅ מה יש כאן?

אתר Flask דינמי מלא שעובד ונגיש מבחוץ!

### תכונות:
- ✅ **דינמי לגמרי** - כתבות נפתחות בדפים נפרדים
- ✅ **נגיש מכל מקום** - ניתן להעלות לאינטרנט
- ✅ **עדכון אוטומטי** - משוך חדשות מ-RSS מידי יום
- ✅ **מסד נתונים** - SQLite לשמירת כתבות
- ✅ **עברית RTL** - מימין לשמאל
- ✅ **מדור הימלאיה 450** - דף נפרד עם תוכן עשיר

## 🚀 הרצה מקומית (1 דקה!)

```bash
# 1. התקן תלויות
pip install -r requirements.txt

# 2. הרץ את השרת
python app.py

# 3. פתח בדפדפן
http://localhost:5000
```

**זהו! האתר רץ!** 🎉

## 🌐 העלאה לאינטרנט (חינם!)

### אופציה 1: Render.com (הכי פשוט)
1. צור חשבון ב-render.com
2. "New Web Service" → חבר ל-GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py`
5. הפעל!

### אופציה 2: PythonAnywhere (חינם לגמרי)
1. pythonanywhere.com
2. Upload files
3. Configure WSGI
4. הפעל

### אופציה 3: Heroku
```bash
heroku create
git push heroku main
```

## 📁 מבנה הקבצים

```
app.py              # השרת הראשי
templates/
  ├── base.html     # Template בסיס
  ├── index.html    # עמוד הבית
  ├── article.html  # עמוד כתבה
  └── himalayan.html # עמוד הימלאיה
requirements.txt    # תלויות Python
news.db            # מסד נתונים (נוצר אוטומטית)
```

## 🔧 כיצד זה עובד?

1. השרת Flask רץ ומחכה לבקשות
2. בפעם הראשונה - מושך חדשות מ-RSS
3. שומר את החדשות ב-SQLite
4. כל כתבה נפתחת בדף נפרד עם URL יחודי
5. עדכון אוטומטי מידי יום ב-8:00

## 🎯 URLs באתר

- `/` - עמוד הבית (רשימת חדשות)
- `/article/1` - כתבה ספציפית
- `/himalayan` - מדור הימלאיה 450
- `/update-now` - עדכון ידני

## ⚙️ הגדרות

ערוך `app.py` לשינוי:
- RSS feeds (שורה 14)
- זמן עדכון (שורה 138)
- Port (שורה 159)

זהו! האתר שלך מוכן! 🚀
