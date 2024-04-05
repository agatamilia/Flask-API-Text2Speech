Create by Agatamilia Text to Speech API flask using gTTS

This API provides functionalities for user authentication, text-to-speech conversion, managing conversion history, searching, and editing entries. It leverages Flask, MongoDB, gTTS, SQLAlchemy, and Flask-Login to achieve these functionalities. API Overview:

1. Database Configuration:
- MongoDB is used as the database to store text-to-speech conversion history.
- SQLAlchemy is configured for user authentication and registration.
  
2. User Authentication:
- Flask-Login is implemented for user authentication.
- Users can register, login, and logout.

3. Endpoints:
/: Redirects to the login page.
/register: Allows users to register by providing a username and password.
/login: Authenticates users based on provided credentials.
/logout: Logs out the currently logged-in user.
/history: Retrieves and displays the conversion history from the MongoDB database.
/convert: Converts the provided text to speech and stores the conversion data in the database. Supports GET and POST methods.
/audio/<entry_id>: Retrieves and plays the audio file associated with the given entry ID.
/edit/<entry_id>: Renders a form to edit the text of a specific entry identified by entry ID. Supports GET and PUT methods.
/search: Allows users to search for specific text entries in the conversion history.
/delete/<entry_id>: Deletes a specific entry from the conversion history. Supports POST method.

4. Text-to-Speech Conversion:
- Utilizes the gTTS library to convert text to speech.
- The converted audio data is stored in the database.

5. Error Handling:
Proper error handling is implemented for various scenarios such as method not allowed, entry not found, etc.

6. Running the Application:
- The Flask application runs on host '0.0.0.0' and port '5000' in debug mode.
Reference: https://www.geeksforgeeks.org/convert-text-speech-python/ and https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/
