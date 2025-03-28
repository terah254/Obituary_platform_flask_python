from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_mysqldb import MySQL
from datetime import datetime
from slugify import slugify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_obituary():
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        date_of_death = request.form['date_of_death']
        content = request.form['content']
        author = request.form['author']
        slug = slugify(f"{name}-{datetime.now().strftime('%Y%m%d')}")

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO obituaries(name, date_of_birth, date_of_death, content, author, slug) "
                "VALUES(%s, %s, %s, %s, %s, %s)",
                (name, date_of_birth, date_of_death, content, author, slug)
            )
            mysql.connection.commit()
            flash('Obituary submitted successfully!', 'success')
            return redirect(url_for('view_obituaries'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()

    return render_template('form.html')

@app.route('/obituaries/search', methods=['GET'])
def search_obituaries():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('view_obituaries'))

    cur = mysql.connection.cursor()
    search_query = f"%{query}%"
    cur.execute("SELECT * FROM obituaries WHERE name LIKE %s OR content LIKE %s", (search_query, search_query))
    results = cur.fetchall()
    cur.close()

    if not results:
        flash('No obituaries found matching your search.', 'info')

    return render_template('view.html', obituaries=results, search_query=query)

@app.route('/obituaries', methods=['GET'])
def view_obituaries():
    # Get the current page number from the query string, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of obituaries to display per page

    # Calculate the offset for the SQL query
    offset = (page - 1) * per_page

    # Fetch the obituaries for the current page
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM obituaries ORDER BY created_at DESC LIMIT %s OFFSET %s", (per_page, offset))
    obituaries = cur.fetchall()

    # Fetch the total number of obituaries to calculate total pages
    cur.execute("SELECT COUNT(*) FROM obituaries")
    total_obituaries = cur.fetchone()['COUNT(*)']
    cur.close()

    # Calculate the total number of pages
    total_pages = (total_obituaries + per_page - 1) // per_page

    return render_template(
        'view.html',
        obituaries=obituaries,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/obituary/<slug>')
def obituary_detail(slug):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM obituaries WHERE slug = %s", (slug,))
    obituary = cur.fetchone()
    cur.close()
    if not obituary:
        flash('Obituary not found.', 'danger')
        return redirect(url_for('view_obituaries'))
    return render_template('obituary_detail.html', obituary=obituary)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate dynamic sitemap.xml"""
    pages = []
    today = datetime.now().date()

    # Static pages
    pages.append({
        'url': url_for('home', _external=True),
        'lastmod': today,
        'changefreq': 'daily',
        'priority': '1.0'
    })
    pages.append({
        'url': url_for('submit_obituary', _external=True),
        'lastmod': today,
        'changefreq': 'monthly',
        'priority': '0.8'
    })
    pages.append({
        'url': url_for('view_obituaries', _external=True),
        'lastmod': today,
        'changefreq': 'daily',
        'priority': '0.9'
    })

    # Dynamic obituary pages
    cur = mysql.connection.cursor()
    cur.execute("SELECT slug, submission_date FROM obituaries ORDER BY submission_date DESC")
    obituaries = cur.fetchall()
    cur.close()

    for obit in obituaries:
        pages.append({
            'url': url_for('obituary_detail', slug=obit['slug'], _external=True),
            'lastmod': obit['submission_date'].date(),
            'changefreq': 'yearly',
            'priority': '0.7'
        })

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

if __name__ == '__main__':
    app.run(debug=True)