from pymongo import MongoClient
from dotenv import load_dotenv
import openai
import os
import datetime
from flask import Flask, render_template, request, jsonify


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
password = os.getenv("MONGODB_PASSWORD")

# MongoDB client setup 
client = MongoClient(f"mongodb+srv://Rohith:{password}@montaigne.c676utg.mongodb.net/?retryWrites=true&w=majority")
db = client["montaigne"] # replace with your database name
conversions_col = db.conversions # change 'conversions' to desired collection name

app = Flask(__name__)

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
            'num_tokens': response['usage']['total_tokens'],
        }
        conversions_col.insert_one(conversion_data)  # insert the conversion data into MongoDB
        return {"result": result}
    except Exception as e:
        print(f"Error in generate function: {str(e)}")
        return {"result": "An error occurred during generation"}
    
def main():
    print("Enter the body text:")
    body = input()
    print("Enter the search terms:")
    search_terms = input()
    print("Enter the theme:")
    theme = input()
    print("Enter the number of words:")
    num_words = int(input())
    print("Enter the market name:")
    market_name = input()
    print("Generating article...")
    result = generate_article(body, search_terms, theme, num_words, market_name)
    print(result["result"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        body = request.form["body"]
        search_terms = request.form["search_terms"]
        theme = request.form["theme"]
        num_words = int(request.form["num_words"])
        market_name = request.form["market"]

        result = generate_article(body, search_terms, theme, num_words, market_name)
        output = {"result": result["result"]}
        return jsonify(output)

    except Exception as e:
        print("Error in generate endpoint: ", e)
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)