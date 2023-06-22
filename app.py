from flask import Flask, render_template, request, jsonify
import openai
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

class Config:
    OPENAI_API_KEY = "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"

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

Base = declarative_base()

# Initialize OpenAI
openai.api_key = app.config["OPENAI_API_KEY"]

class GptTokenUsage(Base):
    __tablename__ = 'token_usage'
    id = Column(Integer, primary_key=True)
    generation_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Path to the SQLite file
db_file = 'sqlite:///token_usage.db'

# Creating engine and binding it to the Base class
engine = create_engine(db_file)
Base.metadata.create_all(engine)

# Create a session to access the database
Session = sessionmaker(bind=engine)

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
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.3,
        )
        print("After GPT-4 API call")
        result = response.choices[0].message['content'].strip()
        num_tokens = response['usage']['total_tokens'] if 'usage' in response and 'total_tokens' in response['usage'] else 0

        # Prepare the output
        output = {"result": result}

        # Calculating the cost
        cost = 0.06 * num_tokens / 1000

        # Insert the details into SQLite database
        session = Session()
        token_entry = GptTokenUsage(generation_tokens=num_tokens,
                                     total_tokens=num_tokens,
                                     cost=cost)
        session.add(token_entry)
        session.commit()

        # Fetch the total tokens and total cost used so far
        total_tokens_so_far = session.query(
            func.sum(GptTokenUsage.total_tokens)).scalar()
        total_cost_so_far = session.query(
            func.sum(GptTokenUsage.cost)).scalar()

        print(f"Tokens used in this generation: {num_tokens}")
        print(f"Cost for this generation: ${cost:.5f}")
        print(f"Total tokens used so far: {total_tokens_so_far}")
        print(f"Total cost so far: ${total_cost_so_far:.5f}")

        session.close()
        
        return output

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

@app.errorhandler(500)
def server_error(e):
    print("Internal server error: ", str(e))
    return jsonify(error='Internal server error'), 500

if __name__ == "__main__":
    app.run(debug=True)