import os
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Article, Video

app = Flask(__name__)

engine = create_engine("sqlite:///data/news.db")
Session = sessionmaker(bind=engine)

@app.route("/")
def index():
    session = Session()
    articles = session.query(Article).filter_by(category="general").order_by(Article.created.desc()).limit(12)
    return render_template("index.html", articles=articles)

@app.route("/himalayan")
def himalayan():
    session = Session()
    articles = session.query(Article).filter_by(category="himalayan").order_by(Article.created.desc()).limit(10)
    videos = session.query(Video).order_by(Video.created.desc()).limit(5)
    return render_template("himalayan.html", articles=articles, videos=videos)

@app.route("/article/<int:id>")
def article(id):
    session = Session()
    article = session.query(Article).get(id)
    return render_template("article.html", article=article)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
