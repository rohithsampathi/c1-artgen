from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import openai
import os
import datetime
from urllib.parse import quote
import boto3
from flask_cors import CORS, cross_origin

# Load environment variables
load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")

# Initialize the Flask application and MongoDB connection
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.config["MONGO_URI"] = f"mongodb+srv://Rohith:{quote(app.config['MONGODB_PASSWORD'])}@montaigne.c676utg.mongodb.net/montaigne?retryWrites=true&w=majority"
mongo = PyMongo(app)
db = mongo.db

# Initialize OpenAI
openai.api_key = app.config["OPENAI_API_KEY"]


def generate_article(body, search_terms, theme, num_words, market_name):
    writing_style = f"""
        You are Montaigne, a writing assistant who writes market intelligence articles in Steve Jobs product launch style. You will be given a supportive body text basing on which you will write an article about the [Theme] of the [Market Name] including the [Search Terms], in [Word Count] words.
        Instructions:
        1. Make the article highly professional and informative, while keeping the language simple and easy to understand.
        2. Include Analysis by experts in the field.
        3. Target audience are business decision makers, investors, CXOs and R&D professionals.
        4. Reader should read the article and request for a sample report of the market from DataM Intelligence.

        MUST Follow rules:
        1. Use the [Search Terms] within the content.
        2. Make the content 100% human-like. Rephrase the provided body completely.
        3. Maintain the [Word Count] for article length.
        4. Do not use robotic and magical words. Avoid using technical jargon.
        5. Make the article world-class and informative by including latest trends and news.
        6. Remove any references as a large language model or chatbot. "DataM Intelligence" alone should be quoted as reference in the entire article

        Content Structure:
        Heading
        \n
        Introduction paragraph giving the market overview
        \n
        Side Heading: Should include the [Search Terms]
        Content:

        [Similarly for 3 more side headings]

        Future of [Market Name] with [Theme]
        [Redirect the reader to download-sample page]

            ------------------------- End of Instructions -------------------------

    """

    # GPT-4 chat model processing with news_content as input
    try:
        print("Before GPT-4 API call")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"{writing_style}"},
                {"role": "user", "content": f"Market Name: {market_name} \n Body: {body} \n Search Terms: {search_terms} \n Theme: {theme} \n Word Count: {num_words} ------------- End of News Content. Start Writing the Article Below -------- \n "},
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.3,
        )
        print("After GPT-4 API call")
        result = response.choices[0].message['content'].strip()
        num_tokens = response['usage']['total_tokens'] if 'usage' in response and 'total_tokens' in response['usage'] else 0

        # Prepare the output
        output = {"result": result}

        # Insert the conversion details into MongoDB
        conversion_data = {
            'timestamp': datetime.datetime.utcnow(),
            'input': {
                'market_name': market_name,
                'search_terms': search_terms,
                'theme': theme,
                'num_words': num_words,
                'body': body,
            },
            'output': result,
            'num_tokens': num_tokens,
        }

        # Try to insert the data into MongoDB
        try:
            mongo.db.articles.insert_one(conversion_data)
        except Exception as e:
            print(f"Failed to insert data into MongoDB: {e}")
            output['db_error'] = str(e)

        return output

    except Exception as e:
        print(f"Error in generate function: {str(e)}")
        return {"result": "An error occurred during generation"}

def get_conversions_col():
    conversions_col = None
    try:
        conversions_col = mongo.db.articles
    except AttributeError as e:
        print("Failed to access MongoDB collection: ", str(e))
    return conversions_col

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
@cross_origin()
def generate():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        body = data.get("body")
        search_terms = data.get("search_terms")
        theme = data.get("theme")
        num_words = int(data.get("num_words"))
        market_name = data.get("market")

        # Use the generate_article function
        result = generate_article(body, search_terms, theme, num_words, market_name)
        output = {"result": result["result"]}

        # Handle potential database error
        if 'db_error' in result:
            output['db_error'] = result['db_error']

        return jsonify(output)

    except Exception as e:
        print("Error in generate endpoint: ", e)
        return jsonify(error=str(e)), 500

@app.errorhandler(500)
def server_error(e):
    print("Internal server error: ", str(e))
    return jsonify(error='Internal server error'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)