# ByteSerenity

ByteSerenity is a Flask web application primarily catering to the mental health, work-life balance, and wellness needs of tech professionals and enthusiasts. Alongside providing a platform for creating, sharing, and discussing tech-related blog posts, it emphasizes topics such as dealing with burnout and seeking work-life balance. ByteSerenity fosters a supportive community where users can connect, share experiences, and learn from each other. With robust user authentication and interactive features like commenting and liking, ByteSerenity aims to facilitate meaningful discussions and mutual growth within the tech industry.

## Features

- **User Authentication**: Users can register an account, log in, and log out securely.
- **Post Creation**: Authenticated users can create new blog posts, including titles, content bodies, tags, and optional images.
- **Post Management**: Users can view, edit, and delete their own posts.
- **Comments**: Users can add comments to blog posts.
- **Tags**: Posts can be tagged with keywords for organization and searchability.
- **Search**: The application provides a search functionality to find posts based on keywords.
- **Like**: Users can like posts, and the application tracks the number of likes for each post.
- **Profile Management**: Users can view and update their profile details, including name, date of birth, biography, email, and profile picture.

## Technologies Used

- **Flask**: Flask is a micro web framework for Python used to develop the application.
- **MySQL**: MySQL is used as the relational database management system.
- **HTML/CSS/JavaScript**: Standard web technologies are used for front-end development.
- **TailwindCSS**: TailwindCSS is used for styling and layout of the application.
- **Jinja2**: Jinja2 templating engine is used for generating dynamic HTML content.
- **Werkzeug**: Werkzeug is a WSGI utility library for Python, which is used for routing and handling requests.
- **Markdown**: Markdown is used for writing README and other documentation files.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Tau-rai/ByteSerenity.git
    ```

2. Navigate to the project directory:

    ```bash
    cd ByteSerenity
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

5. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Set up environment variables:

    ```bash
    export FLASK_APP=app
    export FLASK_ENV=development
    ```

7. Initialize the database:

    ```bash
    flask init-db
    ```

8. Run the application:

    ```bash
    flask run
    ```

The application should now be accessible at [http://localhost:5000](http://localhost:5000).

## Usage

- Visit the homepage to view existing blog posts and search for posts using the search bar.
- Register an account or log in to create new posts, comment on existing posts, and like posts.
- Navigate to your profile page to view and update your profile details.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please submit a pull request or open an issue on GitHub.

## License

No License.

## Authors

- [Taurai Masaire](https://github.com/Tau-rai)
- [Avumile Ndlovu](https://github.com/Aevy21)
