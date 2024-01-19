from playwright.sync_api import sync_playwright, Playwright, Page, ElementHandle
import re


def hover_over_book(element: ElementHandle, page: Page) -> tuple:
    element.hover()
    page.wait_for_timeout(3000)

    author, language = "Unknown author", "Language not found"
    feature_labels = element.query_selector_all(".ty-product-feature__label em")
    for feature_label in feature_labels:
        label_text = feature_label.inner_text()
        match label_text:
            case "Author":
                author_info = feature_label.evaluate("node => node.parentElement.nextElementSibling.querySelector('em').textContent")
                author = author_info.strip() if author_info else "Unknown author"
            case "Language":
                language_info = feature_label.evaluate("node => node.parentElement.nextElementSibling.querySelector('em').textContent")
                language = language_info.strip().lower() if language_info else 'Language not found'
    return author, language


def book_name(element: ElementHandle, page: Page) -> str:
    page.wait_for_timeout(3000)

    try:
        book_name_text = element.query_selector(".ut2-gl__name").inner_text()
    except AttributeError:
        book_name_text = "Unknown book name"
    return book_name_text.strip()


def get_price(element: ElementHandle, page: Page) -> tuple:
    page.wait_for_timeout(3000)

    try:
        old_price_text = element.query_selector(".ty-list-price.ty-nowrap").inner_text()
        old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))
        discounted_price_text = element.query_selector(".ty-price-num").inner_text()
        discount_price = float(format(float(re.search(r"\d+(\.\d+)?", discounted_price_text).group()), ".2f"))

    except AttributeError:
        old_price_text = element.query_selector(".ty-price-num").inner_text()
        old_price = float(format(float(re.search(r"\d+(\.\d+)?", old_price_text).group()), ".2f"))
        discount_price = None
    return old_price, discount_price


def get_discount_sticker(element: ElementHandle, page: Page) -> float:
    page.wait_for_timeout(3000)

    try:
        discount_sticker_text = element.evaluate("""
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


def find_all_books(page: Page) -> list:
    all_books = page.query_selector_all(".ty-column4")
    return all_books


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.libraff.az/kitab/")
    books = find_all_books(page)
    for book in books:
        author, language = hover_over_book(book, page)
        book_name_text = book_name(book, page)
        price = get_price(book, page)
        discount = get_discount_sticker(book, page)
        print(f"Author: {author}, Language: {language}, Book: {book_name_text}, price: {price}, discount: {discount}")
        print("Book is hovered")

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
