import pytest
from bs4 import BeautifulSoup
import requests
import re
from typing import Optional, Dict, List, Any

# Firstly it will be a test for Ali and Nino scraper//
languages = [
        "knigi-na-azerbaydzhanskom-yazyke",
        "knigi-na-russkom-yazyke",
        "knigi-na-angliyskom-yazyke",
        "knigi-na-turetskom-yazyke",
        "books-in-french"
    ]


@pytest.fixture(params=languages)
def setup_module(request) -> BeautifulSoup:
    language = request.param
    page = 2
    page_url = f"https://alinino.az/collection/{language}?page={page}"
    page_content = requests.get(page_url).text
    soup = BeautifulSoup(page_content, "html.parser")
    return soup


@pytest.fixture
def ali_nino_title(setup_module: BeautifulSoup) -> list[str]:
    soup = setup_module
    books_per_page = soup.find_all("div",
                                  class_="product-card-wrapper in-collection cell-2 cell-4-md cell-6-sm cell-6-mc")

    titles = [book.find("div", class_="product-card-title").text.strip()
              if book.find("div", class_="product-card-title")
              else "Unknown Author"
              for book in books_per_page]
    print(titles)
    return titles


@pytest.fixture
def ali_nino_author(setup_module: BeautifulSoup) -> dict[str, list[Any]]:
    soup = setup_module
    books_per_page = soup.find_all("div",
                                  class_="product-card-wrapper in-collection cell-2 cell-4-md cell-6-sm cell-6-mc")

    authors = dict()
    authors_list = []
    for book in books_per_page:
        try:
            author_element = book.find("div", class_="product-card-properties")
            author = author_element.find_all("div", class_="product-card-properties-item")[1].text.strip()
            authors_list.append(author)
        except IndexError:
            pass
    authors["authors_names"] = authors_list
    print(authors)
    return authors


@pytest.fixture
def ali_nino_book_prices(setup_module: BeautifulSoup) -> tuple[tuple[Optional[float], ...]]:
    soup = setup_module
    books_per_page = soup.find_all("div",
                                   class_="product-card-wrapper in-collection cell-2 cell-4-md cell-6-sm cell-6-mc")
    books_prices = tuple()
    for book in books_per_page:
        old_price = None
        discount = None
        new_price = None
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

        price_info = (old_price, discount, new_price)
        books_prices += (price_info,)
    print(books_prices)
    return books_prices


@pytest.fixture
def books_availability(setup_module: BeautifulSoup) -> list[bool]:
    soup = setup_module
    books_per_page = soup.find_all("div",
                                   class_="product-card-wrapper in-collection cell-2 cell-4-md cell-6-sm cell-6-mc")
    availability_list = []
    for book in books_per_page:
        if book.find("span", class_="label not-available"):
            available = False
        else:
            available = True
        availability_list.append(available)
    return availability_list


def test_ali_nino_scraper(ali_nino_title: pytest,
                          ali_nino_book_prices: pytest,
                          ali_nino_author: pytest,
                          books_availability: pytest) -> None:
    assert isinstance(ali_nino_title, list)
    assert all(isinstance(title, str) for title in ali_nino_title)
    assert len(ali_nino_title) >= 42

    # // Here is our checking of books' prices
    assert isinstance(ali_nino_book_prices, tuple)

    for old_price, discount, new_price in ali_nino_book_prices:
        assert isinstance(old_price, (float, type(None)))
        assert isinstance(discount, (float, type(None)))
        assert isinstance(new_price, (float, type(None)))

        if discount is not None:
            assert old_price is not None and new_price is not None
            assert old_price > new_price

    # // Checking authors name
    assert isinstance(ali_nino_author, dict)

    authors_list = ali_nino_author["authors_names"]  # Assuming 'authors' is the key for the list of author names
    for name in authors_list:
        assert isinstance(name, str), "Each name in authors list should be a string"

    # // checking availability . Should be all bools
    assert isinstance(books_availability, list)

    for availability in books_availability:
        assert isinstance(availability, bool)


def test_ali_nino_book_prices(ali_nino_book_prices):
    assert ali_nino_book_prices is not None, "Book prices should not be None"
    assert len(ali_nino_book_prices) > 0, "There should be at least one book price"

