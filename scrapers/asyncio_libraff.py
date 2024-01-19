from playwright.async_api import async_playwright, Playwright, Page, ElementHandle
import asyncio
import re
from databases import Session, TestDb, Base, Books

number_page = 0
books_proceeded = 0
body_selector = ".ty-column4"
# [".ut2-gl__name", ".ty-list-price.ty-nowrap", "ty-price-num", ".ty-pagination__right-arrow"]


async def hover_over_book(element: ElementHandle, page: Page) -> tuple:
    # await page.wait_for_timeout(2000)
    try:
        if await element.wait_for_element_state("enabled", timeout=20000) and await page.wait_for_load_state("domcontentloaded"):
            await page.hover(selector=".ty-column4", timeout=3000)

        author, language = "Unknown author", "Language not found"
        feature_labels = await element.query_selector_all(".ty-product-feature__label em")
        for feature_label in feature_labels:
            label_text = await feature_label.inner_text()
            match label_text:
                case "Author":
                    author_info = await feature_label.evaluate("node => node.parentElement.nextElementSibling.querySelector('em').textContent")
                    author = author_info.strip() if author_info else "Unknown author"
                case "Language":
                    language_info = await feature_label.evaluate("node => node.parentElement.nextElementSibling.querySelector('em').textContent")
                    language = language_info.strip().lower() if language_info else 'Language not found'
        return author, language
    except Exception as e:
        print(f"Error while hovering over book element: {e}")
        return "Unknown author", "Language not found"


async def book_name(element: ElementHandle, page: Page) -> str:
    await page.wait_for_load_state()
    # await page.wait_for_timeout(3000)

    try:
        book_name_element = await element.query_selector(".ut2-gl__name")
        book_name_text = await book_name_element.inner_text()
    except AttributeError:
        book_name_text = "Unknown book name"
    return book_name_text.strip()


async def get_price(element: ElementHandle, page: Page) -> tuple:
    await page.wait_for_load_state()
    # await page.wait_for_timeout(3000)
    old_price, discount_price = None, None
    try:
        old_price_element = await element.query_selector(".ty-list-price.ty-nowrap")

        old_price_text = await old_price_element.inner_text()
        old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))
        discounted_price_element = await element.query_selector(".ty-price-num")
        discounted_price_text = await discounted_price_element.inner_text()
        discount_price = float(format(float(re.search(r"\d+(\.\d+)?", discounted_price_text).group()), ".2f"))

    except AttributeError:
        old_price_element = await element.query_selector(".ty-price-num")
        if old_price_element:
            old_price_text = await old_price_element.inner_text()
            old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))
        discount_price = None
    return old_price, discount_price


async def get_discount_sticker(element: ElementHandle, page: Page) -> float:
    await page.wait_for_load_state()
    # await page.wait_for_timeout(3000)

    try:
        discount_sticker_text = await element.evaluate("""
            (element) => {
                const discount_sticker_elements = element.querySelectorAll(".ab-sticker__name span");
                for (const el of discount_sticker_elements) {
                    if (el.textContent.includes('Discount')) {
                        return el.textContent.trim();
                    }
                }
                return null;  // Return null if no element matches
            }
        """)
        discount_number = float(format(float(re.search(r"\d+", discount_sticker_text).group()), ".2f"))

    except (AttributeError, TypeError):
        discount_number = None
    return discount_number


async def is_available(element: ElementHandle, page: Page) -> bool:
    await page.wait_for_load_state()
    # await page.wait_for_timeout(3000)

    try:
        book_availability = await element.evaluate("""(element) => {
                const outOfStockElement = element.querySelector('.ab-sticker-full_size big');
                return !(outOfStockElement && outOfStockElement.textContent.includes('Out of stock'));
            }""")

    except AttributeError:
        book_availability = None

    return book_availability


async def next_page(page: Page) -> bool:
    await page.wait_for_load_state()
    await page.wait_for_timeout(2000)
    try:
        next_button = await page.query_selector(".ty-pagination__right-arrow")
        if next_button:
            next_page_attribute = await next_button.get_attribute("data-ca-page")
            if next_page_attribute:
                # await page.wait_for_timeout(1500)
                await page.click(".ty-pagination__right-arrow")
                await page.wait_for_timeout(3000)
                await page.wait_for_load_state("domcontentloaded")
                return True
        return False
    except AttributeError as e:
        print(f"Error navigating to the next page: {e}")
        return False


async def find_all_books(page: Page) -> list:
    await page.wait_for_load_state("domcontentloaded")
    all_books = await page.query_selector_all(".ty-column4")
    return all_books


async def process_book(book, page, session: Session):
    global books_proceeded
    await page.wait_for_load_state("domcontentloaded")
    currency = "AZN"
    book_store = "Libraff"
    author, language = await hover_over_book(book, page)
    book_name_text = await book_name(book, page)
    old_price, new_price = await get_price(book, page)
    discount = await get_discount_sticker(book, page)
    book_availability = await is_available(book, page)
    new_book_data = {
        'old_price': old_price,
        'discount': discount,
        'new_price': new_price
    }
    existing_book = session.query(Books).filter_by(
        title=book_name_text,
        author=author,
        language=language,
        store=book_store
    ).first()
    if existing_book:
        print(f"Book {book_name_text} already existed")
        existing_book.available = book_availability
        update_book_details(existing_book, new_book_data)

    else:
        new_book = Books(
            title=book_name_text,
            author=author,
            old_price=old_price if old_price else None,
            discount=discount if discount else None,
            new_price=new_price if new_price else None,
            currency=currency,
            language=language,
            store=book_store,
            available=book_availability
        )
        session.add(new_book)
    books_proceeded += 1


async def check_bodyEl_is_available(page: Page, selector: str) -> bool:
    element = await page.wait_for_selector(selector)
    if not element:
        return False
    else:
        print("Passed")
        return True


def update_book_details(existing_book, new_book_data: dict) -> None:
    fields_to_update = [field for field in new_book_data.keys()]
    for field in fields_to_update:
        if getattr(existing_book, field) != new_book_data[field]:
            setattr(existing_book, field, new_book_data[field])


def page_limit(page: int) -> bool:
    if page == 500:
        return False
    return True


# def skip_page(page: Page, current_page: int) -> None:
#     global number_page
#     print(f"Skipping page {current_page}, moving directly to page {current_page + 2}")
#     page.goto(f"https://www.libraff.az/kitab/{current_page + 2}/")
#     number_page += 2

async def skip_page(page: Page, current_page: int):
    global number_page
    new_page_number = current_page + 2
    await page.goto(f"https://www.libraff.az/kitab/page-{new_page_number}/")
    number_page = new_page_number
    await page.wait_for_load_state("domcontentloaded")


# async def page_number(page: Page) -> None:
#     global number_page
#     current_url = page.url
#
#     number = re.search(r"page-(\d+)", current_url)
#
#     integer = int(number.group(1)) if number else None
#     print(f"The next page is {integer}")
#     if number_page == integer and number_page != 1:
#         await skip_page(page, integer)
#     else:
#         number_page = integer

def page_number(page: Page) -> int:
    current_url = page.url
    number = re.search(r"page-(\d+)", current_url)
    return int(number.group(1)) if number else None


async def process_books_on_page(page: Page, db_session: Session) -> bool:
    global number_page, books_proceeded
    global body_selector
    current_page_number = page_number(page)
    if current_page_number == number_page and number_page != 1:
        await skip_page(page, current_page_number)
    else:
        number_page = current_page_number
    print("Processing books on page")
    print(number_page)

    if await check_bodyEl_is_available(page, body_selector):
        books = await find_all_books(page)
        tasks = [asyncio.create_task(process_book(book, page, db_session)) for book in books]
        await asyncio.gather(*tasks)
    else:
        "The element is not found, unfortunately. Moving on next page!"

    if books_proceeded >= 100:
        db_session.commit()  # Commit after every 100 books
        books_proceeded = 0
    if page_limit(number_page):
        if books_proceeded > 0:
            db_session.commit()
        return await next_page(page)
    # db_session.close()
    return False


async def run(playwright: Playwright, session: Session) -> None:
    global number_page
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.libraff.az/kitab/page-1/")
    await page.wait_for_load_state("domcontentloaded")
    while True:
        if not await process_books_on_page(page, session):
            break

    await context.close()
    await browser.close()


async def main(session: Session):
    async with async_playwright() as playwright:
        await run(playwright, session)

# asyncio.run(main())
