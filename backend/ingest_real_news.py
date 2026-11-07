import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.services.ingestion import run_ingestion_pipeline
from app.models.article import Article

def main():
    print("Starting live RSS news ingestion...")
    with SessionLocal() as db:
        res = run_ingestion_pipeline(db, force_seed=False, max_articles=200)
        print("Ingestion result:", res)
        total = db.query(Article).count()
        print(f"Total articles in SQLite database: {total}")
        
        # Display top 10 most recent articles
        recent = db.query(Article).order_by(Article.published_at.desc()).limit(10).all()
        print("\n--- Top 10 Most Recent Ingested Articles ---")
        for i, a in enumerate(recent, 1):
            print(f"{i}. [{a.source}] {a.title} ({a.sector}) - Symbols: {a.symbols} - Sentiment: {a.sentiment} ({a.sentiment_score:+.2f})")
            print(f"   URL: {a.url}")
            print(f"   Published: {a.published_at}")

if __name__ == "__main__":
    main()

