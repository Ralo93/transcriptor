from flask import Flask, render_template
import threading

app = Flask(__name__)

# Assuming DataStorage is instantiated as `storage` in your main application
storage = None  # Placeholder, will be set by the main app

@app.route('/')
def index():
    word_frequencies = storage.get_word_frequencies()
    return render_template('index.html', word_frequencies=word_frequencies)

def run_web_app(storage_instance):
    global storage
    storage = storage_instance
    app.run(debug=True, use_reloader=False)

# The index.html template should be created in a 'templates' folder within your project directory.
# Example content for the index.html template:
#
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Word Frequencies</title>
# </head>
# <body>
#     <h1>Word Frequencies</h1>
#     <table>
#         <tr>
#             <th>Word</th>
#             <th>Frequency</th>
#         </tr>
#         {% for word, frequency in word_frequencies %}
#         <tr>
#             <td>{{ word }}</td>
#             <td>{{ frequency }}</td>
#         </tr>
#         {% endfor %}
#     </table>
# </body>
# </html>
