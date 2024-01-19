from databases import engine, Base, Session, Books, TestDb

Base.metadata.create_all(engine)


def check_if_book_exists(book_name: str) -> str:
    session = Session()

    # Query for all books with the given title, regardless of the language
    books = session.query(Books).filter(Books.title.ilike(f"%{book_name}%")).all()

    if not books:
        return f"There is no book called {book_name} in any of the available languages."

    book_details = []
    for book in books:
        if book.available:
            book_info = (f"There is a book called {book.title} - {book.author} which is available "
                         f"in the {book.store} for {book.new_price if book.new_price else book.old_price} {book.currency}. "
                         f"The book is in {book.language} language.")
        else:
            book_info = f"There is a book called {book.title} which is not available yet."
        book_details.append(book_info)

    return "\n".join(book_details)


search = input("Enter the book title:")
print(check_if_book_exists(search))



