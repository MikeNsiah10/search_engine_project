from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import traceback#

#initialise flask app
app = Flask(__name__)

#directory where whoosh index is located
index_dir = "indexdir"

@app.route('/')
def home():
     # Render the HTML template for the search form
    return render_template('search_form.html')

#handle internal server error
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

@app.route('/search')
def search():
    # Get the search query from the request parameters
    query = request.args.get('q', '')
    
    if not query:
        return 'No search query provided.'
    #open whoosh index directory
    index = open_dir(index_dir)
    #perform search and return search results
    with index.searcher() as searcher:
        query_parser = QueryParser("content", index.schema)
        query_object = query_parser.parse(query)
        results = searcher.search(query_obj)

        return render_template('search_results.html', query=query, results=results)

#run the flask app in debug mode
if __name__ == '__main__':
    app.run(debug=False)

