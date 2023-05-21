from flask import Flask, request, jsonify, render_template
import openai
from newspaper import Article

app = Flask(__name__)
openai.api_key = "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"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_route():
    url = request.form['news']
    search_terms = request.form['search_terms']
    theme = request.form['theme']
    try:
        news_content = process_url(url.strip())
        news_snippet = generate(news_content, search_terms, theme)
        return jsonify({"result": {"art_output": news_snippet["result"]}})
    except Exception as e:
        return jsonify({"error": f"Error processing URL {url}: {str(e)}"}), 400

def process_url(url):
    article = Article(url)
    article.download()
    article.parse()

    headline = article.title
    body = article.text[:2000]

    content = f"Heading: {headline}\n\nSnippet: {body}\n\n"

    return content


def generate(news_content, search_terms, theme):
    writing_style = f"""

    Your Background:
    You are Montaigne a writing assistant who is a disciple of famous Martin Wolf and greatly influenced by Steve Jobs product launch style working for DataM Intelligence. The above content is a summary of the [product] market report. Write a 600 word article with Side headings of the [search terms] provided. 

    Your Writing Style:
    1. Purpose of this article is elaborate the [theme] and guide on what are the key trends around the [theme].
    2. Keep the content simple and business professional. Cover the trends and news. Include the [search terms] within the content. 
    3. Reader should feel empowered and request for download sample from DataM Intelligence to know more in depth information 
    4. Target audience are business decision makers from procurement, product development, marketing, sales, management and R&D divisions.

    Follow the below Content Structure in the same order:
    1. Heading Title [Should contain long tail keywords]
    2. Introduction paragraph giving the market overview
    3. Side Heading [Should contain the search terms]
    4. Content from the summary [Use search terms and keyword as per SEO norms]
    5. [Similarly for 3 more side headings]
    6. Future Market Outlook [Redirect the reader to download-sample page]

    Rules you MUST follow while writing:
    1. Make the content 100% human-like. Rephrase the content and do not directly use reference information. 
    2. Do not exceed 600 words. 
    3. Do not use robotic sounding words and avoid using technical jargon. 
    4. Add more details and examples to make the article highly informative.
    5. Remove any references as a large language model or chatbot.

    ------------------------- End of Instructions -------------------------

    \n


    """

    # GPT-4 chat model processing with news_content as input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"{writing_style}"},
            {"role": "user", "content": f"{news_content} \n ------------- End of News Content News content -------------- \n Write the article from provided content. Please use the {search_terms} to write the article with the main focus on {theme} \n ---------- Start Writing Below -------- \n "},
        ],
        max_tokens=700,
        top_p=1,
        n=1,
        stop=None,
        temperature=0.8,
    )

    result = response.choices[0].message['content'].strip()
    return {"result": result}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creating all database tables
    app.run(debug=True)
