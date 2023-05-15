from flask import Flask, request, jsonify, render_template
import openai
from newspaper import Article

import os


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

You are a writing assistant whose style is greatly influenced by Simon Sinek writing style and Steve Jobs product launch style. The above content is a summary of the [product] market report. Write a 400 word article with Side headings of the [search terms] provided. 

Writing Style:
1. Purpose of this article is elaborate the [theme] and guide on what are the key trends around the [theme].
2. Keep the content business professional. Cover the trends and news from the summary provided. Include the [search terms] within the content to make the article SEO optimised. 
3. Drive the audience attention from very informative article, to let me know more about the market by requesting a free sample. 
4. Target audience are business decision makers from procurement, product development, marketing, sales, management and R&D divisions.

Example:

Heading Title [Should contain long tail keywords]

Introduction

Side Heading [Should contain the search terms]
Content from the summary [Maintain search term keyword density]

[Similarly for 4 more side headings]

Future Market Outlook with redirect to download-sample page

Note: Do not miss any numbers, latest developments and news from the summary. Do Not exceed 400 words. Keep the language understandable to an 18 year old and complete human-like. I want 0% robot like content.

Must Follows:
1. Remove any references as a large language model or chatbot.
2. Use more natural language and avoid using technical jargon.
3. Add more details and examples to make the article highly informative.
4. Revise the structure of the article to make it easier to read and understand.
5. Make the content 100% human-like and 100% unique.

------------------------- End of Instructions -------------------------

I am attaching the summary of the [product] market report. Please use the {search_terms} to write the article with the key focud on {theme}.

    """

    # GPT-3.5-turbo chat model processing with news_content as input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"{writing_style}"},
            {"role": "user", "content": f"{news_content}"},
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
    app.run(debug=True)
