from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Web Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #ffeef8; padding: 20px; }
        h1 { text-align: center; color: #d5006d; }
        label, select, input, button { display: block; margin: 10px auto; width: 300px; }
        button { background-color: #ff4081; color: white; padding: 10px; cursor: pointer; border: none; }
        .output-container { margin-top: 20px; padding: 10px; background-color: white; border: 1px solid #f1a7c3; }
        .quote { border: 1px solid #f1a7c3; padding: 5px; margin: 5px 0; }
        #loading { display: none; text-align: center; color: #ff4081; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Web Scraper</h1>        
    
    <label for="website-select">Select Website:</label>
    <select id="website-select" onchange="updateURL()">
        <option value="https://books.toscrape.com/">Books to Scrape</option>
        <option value="https://quotes.toscrape.com/">Quotes to Scrape</option>
    </select>

    <label for="url">Enter URL:</label>
    <input type="text" id="url" value="https://books.toscrape.com/" />

    <label for="category">Select Category:</label>
    <select id="category"></select>
    
    <button onclick="scrapeData()">Scrape</button>
    
    <div id="loading">Please wait... Loading...</div>
    
    <div class="output-container" id="output">
        <h2>Scraped Output:</h2>
        <div id="output-content"></div>
    </div>

    <script>
        function updateURL() {
            const selectedWebsite = document.getElementById('website-select').value;
            document.getElementById('url').value = selectedWebsite;

            const categorySelect = document.getElementById('category');
            categorySelect.innerHTML = '';

            const categoriesForBooks = [
                { value: ".product_pod", text: "Books" },
                { value: "h3 a", text: "Book Titles" },
                { value: ".price_color", text: "Book Prices" }
            ];
            
            const categoriesForQuotes = [
                { value: ".quote", text: "Quotes" },
                { value: ".author", text: "Authors" }
            ];

            const categories = selectedWebsite.includes('books') ? categoriesForBooks : categoriesForQuotes;
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.value;
                option.textContent = category.text;
                categorySelect.appendChild(option);
            });
        }

        async function scrapeData() {
            const url = document.getElementById('url').value;
            const category = document.getElementById('category').value;
            const loadingMessage = document.getElementById('loading');
            const outputContent = document.getElementById('output-content');

            // Display the loading message
            loadingMessage.style.display = 'block';
            outputContent.innerHTML = '';

            const response = await fetch('/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, category: category })
            });
            const result = await response.json();

            // Hide the loading message
            loadingMessage.style.display = 'none';

            // Display the scraped data
            outputContent.innerHTML = result.data || 'No data found';
        }

        // Initialize with the default categories for the first website
        updateURL();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    category = data.get('category')

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        elements = soup.select(category)
        scraped_data = "<br>".join([element.get_text(strip=True) for element in elements if element.get_text(strip=True)])

        return jsonify({'data': scraped_data or "No data found."})
    except requests.exceptions.RequestException as e:
        return jsonify({'data': f"Error: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
