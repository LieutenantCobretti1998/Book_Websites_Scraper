import asyncio
from scrapers import ali_nino, asyncio_libraff    # Import your scraping function
from databases import engine, Base, Session, engine  # Import from databases.py
from sqlalchemy.orm import sessionmaker
# Create database tables if they don't exist
# Base.metadata.create_all(engine)
SessionLocal1 = sessionmaker(bind=engine)
SessionLocal2 = sessionmaker(bind=engine)


async def main() -> None:
    # Your languages list
    languages = [
        "knigi-na-azerbaydzhanskom-yazyke",
        "knigi-na-russkom-yazyke",
        "knigi-na-angliyskom-yazyke",
        "knigi-na-turetskom-yazyke",
        "books-in-french"
    ]
    aliNinoScraper = ali_nino.aliNinoBookScraper
    libraff_scraper = asyncio_libraff.main
    # Database session
    db_session_1 = SessionLocal1()
    db_session_2 = SessionLocal2()

    try:
        # Scraping and adding data to the database
        # tasks = [asyncio.create_task(libraff_scraper(db_session_1))]
        # tasks = []
        # tasks.extend([asyncio.create_task(aliNinoScraper(language, db_session_2)) for language in languages])
        # await asyncio.gather(*tasks)

        # for language in languages:
        #     await aliNinoScraper(language, db_session_2)
        #

        await libraff_scraper(db_session_1)

    finally:
        # Close the sessions
        db_session_1.close()
        db_session_2.close()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())

