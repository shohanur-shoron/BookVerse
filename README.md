# BookVerse

BookVerse is a comprehensive web application for book lovers. It allows users to discover new books, track their reading progress, get personalized recommendations, and interact with a community of readers. The platform also integrates AI-powered features to enhance the user experience.

## Features

*   **User Authentication:** Secure user registration and login system.
*   **User Profiles:** Personalized user profiles with profile pictures, bios, and reading interests.
*   **Book Management:**
    *   Browse a vast catalog of books.
    *   View detailed information for each book, including author, category, and description.
    *   Add books to your reading list (e.g., "Currently Reading", "Want to Read", "Read").
    *   Mark books as favorites.
*   **Community and Interaction:**
    *   Leave comments and reviews for books.
    *   Sentiment analysis of comments to gauge reader feedback.
*   **Reading Tracking:**
    *   Track your reading progress for books you are currently reading.
    *   View your reading history and recently viewed books.
*   **Events:**
    *   Create and view events related to books and reading.
*   **AI-Powered Features:**
    *   **Book Recommendations:** Get personalized book recommendations based on your reading history and interests.
    *   **AI Agent:** An interactive AI agent to help you find books and answer your questions.
    *   **Image Book Search:** Search Book using the book cover image.
    *   **Comment Sentiment Analysis:** Check the sentiment of the comment text.
*   **Search:**
    *   Powerful search functionality to find books, authors, and categories.
    *   Search suggestions to improve the user experience.

## Tech Stack

*   **Backend:**
    *   Python
    *   Django
    *   Django REST Framework (for APIs)
*   **Frontend:**
    *   HTML
    *   CSS (with custom stylesheets)
    *   JavaScript
*   **Database:**
    *   SQLite (for development)
*   **Machine Learning / AI:**
    *   TensorFlow / Keras 
    *   Scikit-learn
    *   Numpy
*   **Other Libraries:**
    - Pillow (for image handling)
    - and others from `requirements.txt`

## Project Structure

The project is organized into several Django apps:

*   `BookVerse/`: The main project directory containing settings and project-level URL configurations.
*   `agent/`: Handles the AI agent features.
*   `book/`: Contains models, views, and logic for books, authors, comments, and events.
*   `mainpages/`: Manages the main pages of the application like the homepage.
*   `users/`: Responsible for user authentication, profiles, and user-related data.
*   `static/`: Contains static assets like CSS, JavaScript, and images.
*   `template/`: Holds the HTML templates for the application.
*   `media/`: Stores user-uploaded media files (like profile pictures or book covers).

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd "BookVerse"
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    env\Scripts\activate  # On Linux, use `source env\bin\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

    The application will be available at `http://127.0.0.1:8000/`.

## Usage

After starting the server, you can:
- Create an account or log in.
- Browse books on the homepage.
- Use the search bar to find specific books or authors.
- Click on a book to view its details and leave a comment.
- Update your profile and reading interests.
- Interact with the AI agent for recommendations.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.

## License

This project is licensed under the MIT License.
