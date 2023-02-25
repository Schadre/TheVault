from flask import Blueprint, request, jsonify, render_template, redirect, flash
from flask_login import current_user, login_required
from helpers import token_required
from models import db, User, Book, book_schema, books_schema
import requests 

site = Blueprint('site', __name__, template_folder='site_templates')

@site.route('/')
def home():
    return render_template('index.html')

@site.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@site.route('/books')
def books():
    # Query the database for all books and serialize them using the book schema
    all_books = Book.query.all()
    serialized_books = books_schema.dump(all_books)

    # Render the books.html template with the serialized list of books
    return render_template('books.html', books=serialized_books)


@site.route('/add', methods=['POST'])
@login_required
def add():
    # Get the ISBN from the form data
    isbn = request.form.get('isbn')

    # Make a request to the Open Library API to get book data for the ISBN
    url = f'https://openlibrary.org/isbn/{isbn}.json'
    response = requests.get(url)

    # Parse the API response data into a Python object
    book_data = response.json()

    # Extract the book data fields using the `get()` method with a default value
    title = book_data.get('title', '')
    author = book_data.get('by_statement', '')
    description = book_data.get('description', '')
    cover_image_url = book_data.get('cover', '')

    # Create a new book object using the extracted data and the current user ID
    user_id = current_user.id
    new_book = Book(title=title, author=author, description=description,
                    cover_image_url=cover_image_url, isbn=isbn, user_id=user_id)

    # Add the book to the database and commit the transaction
    db.session.add(new_book)
    db.session.commit()

    # Query the database for all books and serialize them using the book schema
    books = Book.query.all()
    books_json = books_schema.dumps(books)

    # Render the books.html template with the updated list of books
    return render_template('books.html', books=books)

@site.route('/books/<isbn>', methods=['GET', 'POST', 'DELETE'])
@login_required
def delete(isbn):
    # Get the current user's ID
    user_id = current_user.id

    # Query the database for the book with the specified ID and user ID
    book = Book.query.filter_by(isbn=isbn, user_id=user_id).first()

    # If the book is not found, flash an error message and redirect to the books page
    if not book:
        flash('You do not have permission to delete this book.')
        return redirect('/books')

    # If the book is not the user's, flash an error message and redirect to the books page
    if book.user_id != user_id:
        flash('You do not have permission to delete this book.')
        return redirect('/books')

    # Delete the book from the database and commit the transaction
    db.session.delete(book)
    db.session.commit()

    # Flash a success message and redirect the user back to the books page
    flash('Book deleted successfully')
    return redirect('/books')



@site.route('/search')
def search():
    title = request.args.get('title', '')
    url = f'https://openlibrary.org/search.json?q={title}'
    response = requests.get(url)
    data = response.json()
    books = []
    for doc in data['docs']:
        book = {
            'isbn': doc.get('isbn', [''])[0],
            'title': doc.get('title', ''),
            'author': doc.get('author_name', [''])[0]
        }
        books.append(book)
    return render_template('search.html', books=books)
