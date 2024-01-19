from databases import Session, Books, engine
from bs4 import BeautifulSoup
import re
import aiohttp
from sqlalchemy.orm import sessionmaker
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0',
    "Connection": "Close"
}

session_local = sessionmaker(bind=engine)
books_proceeded = 0


async def aliNinoBookScraper(language: str, db_session: Session) -> None:
    global books_proceeded
    timeout = aiohttp.ClientTimeout(total=30000)
    async with aiohttp.ClientSession(timeout=timeout,
                                     headers=headers) as session:
        url = f"https://alinino.az/collection/{language}"
        async with session.get(url) as response:
            response_text = await response.text()

            # Here is our beautiful soup for total pages
            soup = BeautifulSoup(response_text, "html.parser")
            pages = soup.select("li.pagination-item:not(.hidden-md)")
            total_pages = int(pages[-1].text.strip() if pages else None)
            print(total_pages)

            for page in range(1, total_pages + 1):
                print(f"Page: {page}")
                page_url = f"https://alinino.az/collection/{language}?page={page}"
                async with session.get(page_url) as page_response:
                    page_content = await page_response.text()
                    soup = BeautifulSoup(page_content, "html.parser")
                    books_perPage = soup.find_all("div",
                                                        class_="product-card-wrapper in-collection cell-2 cell-4-md cell-6-sm cell-6-mc")

                    for book in books_perPage:
                        try:
                            title = book.find("div", class_="product-card-title").text.strip()
                            print(title)
                        except AttributeError:
                            title = "Unknown book name"

                        author_name = "Unknown author"
                        old_price = None
                        discount = None
                        new_price = None
                        available = None
                        currency = "AZN"
                        book_store = "Ali and Nino"
                        match language:
                            case "knigi-na-azerbaydzhanskom-yazyke":
                                book_language = "aze"
                            case "knigi-na-russkom-yazyke":
                                book_language = "rus"
                            case "knigi-na-angliyskom-yazyke":
                                book_language = "eng"
                            case "knigi-na-turetskom-yazyke":
                                book_language = "tur"
                            case "books-in-french":
                                book_language = "fr"
                            case _:
                                book_language = None
                        try:
                            author_element = book.find("div", class_="product-card-properties")
                            author = author_element.find_all("div", class_="product-card-properties-item")[1].text.strip()
                            author_name = author
                        except IndexError:
                            pass
                        print(author_name)

                        try:
                            discount_text = book.find("div", class_="discount").text.strip()
                            if discount_text:
                                old_price_text = book.find("div", class_="oldprice").text.strip()
                                old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))
                                discount = float(format(float(re.search(r"\d+(\.\d+)?", discount_text).group()), ".2f"))
                                new_price_text = book.find("div", class_="price in-card").text.strip()
                                new_price = float(format(float(re.search(r"\d+(\.\d+)?", new_price_text).group()), ".2f"))

                        except AttributeError:
                            old_price_text = book.find("div", class_="price in-card").text.strip()
                            old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))

                        if book.find("span", class_="label not-available"):
                            available = False
                        else:
                            available = True
                        print(old_price, discount, new_price, currency)
                        print(f"Page {page} is scraped")

                        new_book_data = {
                            'old_price': old_price,
                            'discount': discount,
                            'new_price': new_price
                        }

                        existing_book = db_session.query(Books).filter_by(
                            title=title,
                            author=author_name,
                            language=book_language,
                            store=book_store
                        ).first()
                        if existing_book:
                            print(f"Book {title} already existed")
                            existing_book.available = available
                            update_book_details(existing_book, new_book_data)
                            books_proceeded += 1
                        else:
                            new_book = Books(
                                title=title,
                                author=author_name,
                                old_price=old_price if old_price else None,
                                discount=discount if discount else None,
                                new_price=new_price if new_price else None,
                                currency=currency,
                                language=book_language,
                                store=book_store,
                                available=available
                            )
                            db_session.add(new_book)
                            books_proceeded += 1
                        print(books_proceeded)
                        if books_proceeded == 100:
                            db_session.commit()
                            print("Commited")
                            books_proceeded = 0

                    if books_proceeded > 0:
                        db_session.commit()
                        print(f"Remaining books committed: {books_proceeded}")
                        # books_proceeded = 0  # Reset the counter
                    if page == total_pages:
                        db_session.commit()
                        break  # No more books on this page, exit the loop


def update_book_details(existing_book: object, new_book_data: dict) -> None:
    fields_to_update = [field for field in new_book_data.keys()]
    for field in fields_to_update:
        if getattr(existing_book, field) != new_book_data[field]:
            setattr(existing_book, field, new_book_data[field])
