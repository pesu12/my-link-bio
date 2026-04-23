from flask import Flask, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NOT_AVAILABLE = "Not Available"


# In-memory store for submitted links.
links = [
    {
        "name": "GitHub",
        "url": "https://github.com",
        "title": NOT_AVAILABLE,
        "description": NOT_AVAILABLE,
        "image_url": NOT_AVAILABLE,
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com",
        "title": NOT_AVAILABLE,
        "description": NOT_AVAILABLE,
        "image_url": NOT_AVAILABLE,
    },
    {
        "name": "X",
        "url": "https://x.com",
        "title": NOT_AVAILABLE,
        "description": NOT_AVAILABLE,
        "image_url": NOT_AVAILABLE,
    },
]


def fetch_link_metadata(site_url):
    """Fetch Open Graph metadata and provide defaults when tags are missing."""
    metadata = {
        "title": NOT_AVAILABLE,
        "description": NOT_AVAILABLE,
        "image_url": NOT_AVAILABLE,
    }

    try:
        response = requests.get(site_url, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('meta', attrs={'property': 'og:title'})
        description_tag = soup.find('meta', attrs={'property': 'og:description'})
        image_tag = soup.find('meta', attrs={'property': 'og:image'})

        if title_tag and title_tag.get('content'):
            metadata['title'] = title_tag.get('content').strip()
        if description_tag and description_tag.get('content'):
            metadata['description'] = description_tag.get('content').strip()
        if image_tag and image_tag.get('content'):
            metadata['image_url'] = image_tag.get('content').strip()
    except requests.RequestException:
        # Keep default "Not Available" values when metadata cannot be fetched.
        pass

    return metadata


@app.route('/')
def home():
    return render_template('index.html', links=links)


@app.route('/add', methods=['POST'])
def add_link():
    site_name = request.form.get('site_name', '').strip()
    site_url = request.form.get('site_url', '').strip()

    if site_name and site_url:
        metadata = fetch_link_metadata(site_url)
        links.append(
            {
                "name": site_name,
                "url": site_url,
                "title": metadata['title'],
                "description": metadata['description'],
                "image_url": metadata['image_url'],
            }
        )

    return redirect(url_for('home'))


@app.route('/edit/<int:link_index>', methods=['GET', 'POST'])
def edit_link(link_index):
    # Only allow edits when the selected link exists in memory.
    if not 0 <= link_index < len(links):
        return redirect(url_for('home'))

    if request.method == 'POST':
        site_name = request.form.get('site_name', '').strip()
        site_url = request.form.get('site_url', '').strip()

        if site_name and site_url:
            metadata = fetch_link_metadata(site_url)
            links[link_index] = {
                "name": site_name,
                "url": site_url,
                "title": metadata['title'],
                "description": metadata['description'],
                "image_url": metadata['image_url'],
            }

        return redirect(url_for('home'))

    return render_template('edit.html', link=links[link_index], link_index=link_index)


@app.route('/delete/<int:link_index>', methods=['POST'])
def delete_link(link_index):
    # Remove the selected link index when it exists in the in-memory list.
    if 0 <= link_index < len(links):
        links.pop(link_index)

    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
