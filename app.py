from flask import Flask, request, jsonify, render_template
import openai
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
        if not news_content:
            return jsonify({"error": f"Couldn't process URL {url}. Make sure the input is a valid URL with appropriate content."}), 400
        print("Before generate function")
        news_snippet = generate(news_content, search_terms, theme)
        print("After generate function")
        return jsonify({"result": {"art_output": news_snippet["result"]}})
    except Exception as e:
        return jsonify({"error": f"Error processing URL {url}: {str(e)}"}), 400

def process_url(url):
    try:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        print(f"URL: {url}")
        driver.get(url)
        time.sleep(10)  # Allow the page to load
        html_content = driver.page_source
        print(f"HTML content length: {len(html_content)}")

        soup = BeautifulSoup(html_content, 'html.parser')

        headline = soup.find('h1').text.strip() if soup.find('h1') else "Not found"
        print(f"Headline: {headline}")

        # Search the body content and find all paragraphs
        body = soup.body
        paragraphs = body.find_all('p') if body else []
        print(f"Paragraphs: {len(paragraphs)}")

        # Handle NoneType text in case of empty paragraph tags
        content_body = "\n\n".join([p.text.strip() if p.text is not None else "" for p in paragraphs])
        print(f"Body: {content_body}")

        content = f"Heading: {headline}\n\nSnippet: {content_body}\n\n"

        driver.quit()

        return content
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return None


def generate(news_content, search_terms, theme):
    writing_style = f"""
        You are Montaigne, a writing assistant who learnt writing from Simon Sinek and greatly influenced by Steve Jobs product launch style. The [news content] is a summary of the product market research. Your purpose is to write a 750 word article from the news content to emphasize the {theme} of the given product market.
        Writing Style:
        1. Do not retain the structure of input. Modify the entire content and side headings to make the article highly professional and informative
        2. Keep the content simple and business professional. Include latest trends and news. Include the [search terms] within the content. 
        3. Target audience are business decision makers from procurement, product development, marketing, sales, management and R&D divisions.
        4. Reader should find the article informative and request for a sample report of the [news-content] market from DataM Intelligence.

        MUST Follow rules:
        1. Make the content 100% human-like. Rephrase the source content completely
        2. Do not end the article abruptly. Do not exceed 800 words.
        3. Do not use robotic sounding words and avoid using technical jargon. 
        4. Add more details and examples to make the article highly informative.
        5. Remove any references as a large language model or chatbot. "DataM Intelligence" alone should be quoted as reference in the entire article

        Content Structure:
        Heading Title [Should contain long tail keywords]
        \n
        Introduction paragraph giving the market overview
        \n
        Side Heading: Should include the phrases from {search_terms}
        Content: Should elaborate the side headings using the text from [news content]

        [Similarly for more side headings]

        Future Market Outlook 
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
                {"role": "user", "content": f"{news_content} \n ------------- End of News Content. Start Writing the Article Below -------- \n "},
            ],
            max_tokens=1250,
            top_p=1,
            n=1,
            stop=None,
            temperature=1.0,
        )
        print("After GPT-4 API call")

        result = response.choices[0].message['content'].strip()
        return {"result": result}
    except Exception as e:
        print(f"Error in generate function: {str(e)}")
        return {"result": "An error occurred during generation"}

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
