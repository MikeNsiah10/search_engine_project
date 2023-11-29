from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import traceback

app = Flask(__name__)

INDEX_DIR = 'indexdir'

@app.route('/')
def home():
    return render_template('search_form.html')

@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    if not query:
        return 'No search query provided.'

    ix = open_dir(INDEX_DIR)
    with ix.searcher() as searcher:
        query_parser = QueryParser("content", ix.schema)
        query_obj = query_parser.parse(query)
        results = searcher.search(query_obj)

        return render_template('search_results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
