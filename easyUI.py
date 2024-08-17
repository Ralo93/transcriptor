from flask import Flask, render_template_string, send_file, request
from DataStorage import DataStorage
from flask import Flask, render_template_string, jsonify
import plotly.graph_objs as go
import plotly.io as pio
from deep_translator import GoogleTranslator as Translator


#TODO: Add a filter mechanism for only your voice
#TODO: Add a voice smoothing mechanism, a way to remove the noise from the audio, cut the silence
#TODO Check for privacy issues, make sure the data is not stored in the cloud
#TODO Check if the collected words are real words and wether they got translated correctly
#TODO: Speech Consistency Check:

#speech_trigger_count: A counter that tracks the number of consecutive chunks where speech is detected. The triggered flag is only set to True when speech is detected over a sufficient number of consecutive chunks (controlled by self.speech_trigger_count).
#Speech Chunk Counting:

#The speech_chunk_count is incremented every time a chunk contains speech. If enough consecutive chunks contain speech, the recording starts.
#Avoiding Premature Triggering:

#By requiring multiple consecutive chunks of speech before triggering, we reduce the chances of starting recording due to short noises or brief utterances that aren't part of the intended speech.
#Resetting Speech Chunk Count:

#The speech_chunk_count is reset to 0 when no speech is detected, ensuring that the system is ready to detect a new speech segment correctly.

class UI:
    def __init__(self, word_data=None):
        # Initialize with an empty list if no data is provided
        self.word_data = word_data if word_data is not None else []
        self.translator = Translator(source='auto', target='fr')

    def set_word_data(self, word_data):
        self.word_data = word_data

    def create_bar_graph(self):
        words, counts = zip(*self.word_data)  # Unpack the word list into two lists

        fig = go.Figure(data=[
            go.Bar(x=counts, y=words, orientation='h', marker=dict(color='skyblue'))
        ])

        fig.update_layout(
            title='Word Frequency',
            xaxis=dict(title='Frequency'),
            yaxis=dict(title='Words', automargin=True),
            template='plotly_white',
            height=800,
            width=1200
        )

        graph_json = pio.to_json(fig)
        return graph_json

    def create_top10_bar_graph(self):
        if not self.translator:
            raise ValueError("Translator is not provided.")

        # Sort word data by frequency in descending order and take the top 10
        top10 = sorted(self.word_data, key=lambda x: x[1], reverse=True)[:10]
        words, counts = zip(*top10)

        # Translate words to French using deep_translator's GoogleTranslator
        translated_words = [self.translator.translate(word) for word in words]

        # Combine original and translated words for the y-axis
        combined_labels = [f"{word} ({translated})" for word, translated in zip(words, translated_words)]

        fig = go.Figure(data=[
            go.Bar(x=counts, y=combined_labels, orientation='h', marker=dict(color='lightcoral'))
        ])

        fig.update_layout(
            title='Top 10 Most Frequent Words (Original and Translated to French)',
            xaxis=dict(title='Frequency'),
            yaxis=dict(title='Words (Original and French)', automargin=True),
            template='plotly_white',
            height=600,
            width=800
        )

        graph_json = pio.to_json(fig)
        return graph_json


app = Flask(__name__)
ui = UI()

@app.route('/')
def index():
    return render_template_string('''
        <h1>Word Frequency Bar Graph</h1>
        <div id="bar-graph"></div>
        <div id="top10-graph"></div>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script>
            fetch('/graph').then(response => response.json()).then(data => {
                Plotly.newPlot('bar-graph', data.data, data.layout);
            });

            fetch('/top10_graph').then(response => response.json()).then(data => {
                Plotly.newPlot('top10-graph', data.data, data.layout);
            });
        </script>
    ''')

@app.route('/graph')
def graph():
    if not ui.word_data:
        return jsonify({"error": "No data provided"}), 400
    graph_json = ui.create_bar_graph()
    return graph_json

@app.route('/top10_graph')
def top10_graph():
    if not ui.word_data:
        return jsonify({"error": "No data provided"}), 400
    graph_json = ui.create_top10_bar_graph()
    return graph_json

@app.route('/update_data', methods=['POST'])
def update_data():
    # Expecting JSON input with the word data
    word_data = request.json.get('word_data', [])
    if not word_data:
        return "Invalid or missing word data", 400

    ui.set_word_data(word_data)
    return "Data updated successfully", 200


def main2():
    data_storage = DataStorage()
    frequencies = data_storage.get_word_frequencies()
    print(frequencies)

    # Set the data in the UI object
    ui.set_word_data(frequencies)

    # Start the Flask app
    app.run(debug=True)


if __name__ == "__main__":
    main2()


