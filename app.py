from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_images(search_keyword):
    base_url = "https://hotnakedwomen.com"
    search_url = f"{base_url}/ru/search/{search_keyword}/"

    response = requests.get(search_url)
    response.raise_for_status()
    main_soup = BeautifulSoup(response.text, "html.parser")

    hrefs = []
    grid_divs = main_soup.find_all("div", class_="grid")
    for div in grid_divs:
        links = div.find_all("a", href=True)
        for a in links:
            href = a["href"]
            if href.startswith("http"):
                hrefs.append(href)
            else:
                hrefs.append(base_url + href)
            if len(hrefs) >= 2:
                break
        if len(hrefs) >= 2:
            break

    result = {}
    for idx, link in enumerate(hrefs, start=1):
        page_resp = requests.get(link)
        page_resp.raise_for_status()
        page_soup = BeautifulSoup(page_resp.text, "html.parser")

        image_links = []
        grids = page_soup.find_all("div", class_="grid")
        for grid in grids:
            for a in grid.find_all("a", href=True):
                href = a["href"]
                if any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                    if href.startswith("http"):
                        image_links.append(href)
                    else:
                        image_links.append(base_url + href)

        image_links = list(dict.fromkeys(image_links))
        result[f"image_set_{idx}"] = image_links

    return result

@app.route("/scrape", methods=["POST"])
def scrape_endpoint():
    data = request.get_json(force=True)
    keyword = data.get("keyword")
    if not keyword:
        return jsonify({"error": "Missing 'keyword' in request body"}), 400

    try:
        result = scrape_images(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
