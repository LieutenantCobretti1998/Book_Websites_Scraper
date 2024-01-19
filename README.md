**Book Scraper Project**

**Description**

This project is a sophisticated book scraper tool designed to gather comprehensive information about books from several prominent websites in Azerbaijan, such as Ali & Nino, Libraff, and Book Center. It's built to create a detailed database with various columns, including title, author, discount price, and original price. I have almost 50000 books which scraped for less than 60 minutes.



**Key Features**

**Data Scraping**: Efficiently scrapes book data from multiple sources.

**Asynchronous Processing**: Utilizes asyncio and aiohttp for non-blocking data processing.

**Data Parsing**: Employs BeautifulSoup4 (bs4) for parsing HTML.

**Playwright Library**: Leverages Playwright for robust, browser-based scraping.

**Database Integration**: Organizes scraped data into a structured database.

**Database Management**: Leverages SQLite and SQLAlchemy for database creation and management.

**Testing**: First-time application of pytest for testing various aspects of the project.


**Learning Outcomes**

Mastery of asynchronous programming in Python.

Enhanced script efficiency through the use of asyncio.

Proficiency in web scraping, data parsing, and database management.

Introduction and application of unit testing with pytest.


**Installation**

Python 3.12
Pip 3.21.3
Dependencies



**Usage**
To use the book scraper, follow these steps:

Clone the Repository:

bash
Copy code
git clone [URL to my repository]
cd [repository name]
Set Up Environment:

**It's recommended to use a virtual environment:**

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Running the Scraper:

To start the scraper, use the following command:
bash
Copy code
python main.py  # Replace with your main script file
The script will scrape data and store it in the SQLite database using SQLAlchemy models.
Access the SQLite database using any SQLite database viewer, or query the database within your Python scripts.

**Contributing**

Contributions to the Book Scraper project are welcome! If you have ideas for improvements or have found a bug, here's how you can contribute:

Report Issues: Use the GitHub Issues page to report bugs or suggest enhancements.
Submit Pull Requests: If you've fixed a bug or added a new feature, submit a pull request with a clear description of the changes.
Code Review: Review pull requests submitted by others.
Documentation: Improvements or updates to documentation are highly appreciated.


