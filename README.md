# flask_query_api

This repository contains for a RESTful API based on Flask and Flask-RESTPlus to do a text search based on api query.

## Requirements
Python 3

## Installation and Usage (AWS EC2 Ubuntu)

```
$ sudo apt-get install python3 python3-venv python3-pip
$ cd /path/to/my/workspace/
$ git clone https://github.com/daviwu/flask_query_api
$ cd flask_query_api
$ pyvenv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
$ (venv) export PYTHONPATH=.:$PYTHONPATH
$ (venv) python3 flask_query_api/app.py &
$ (venv) curl -X GET --header 'Accept: application/json' 'http://localhost:8800/api/query/Now%20is'
$ (venv) python3 flask_query_api/test/unit_tests.py
$ (venv) fg
$ (venv) <Ctrl-C>
$ (venv) deactivate
$
```
There are two ways to run a query, a sequential search

```
http://localhost:8800/api/query/{Your search query}
```

Or a Trie search
```
http://localhost:8800/api/query_trie/{Your search query}
```

For example
```
http://localhost:8800/api/query/Now is
http://localhost:8800/api/query_trie/Now is
```

For the trie search, you cannot do multi-line search. 

For the sequential search, you can search across 2 lines, by using "\n". 
If entered directly in the browser, the "\n" needs to be url encoded. 
So "\n" becomes "%0A" 

For example, to search for "able\nto"
```
http://localhost:8800/api/query/able%0Ato
```

You can also use the "Try it out!" button provided by the Swagger API documentation, like
```
http://localhost:8800/api/

GET /query/{query_text} 

Parameters

Parameter   Value
-------------------
query_text  able%0Ato  
```

Remember in the "Value" textbox, you have to enter the urlencoded "able%0Ato", and not "able\nto", since Swagger will escape encode backslash "\" to "%5c" and not "\n" to "%0A". 

Searching across more than 2 lines, e.g., `text1\ntext2\ntext3` is not implemented, but can be done with slight modification of the code. 

The algorithm will search any .txt files under `flask_query_api/api/query/files`. However do not put more then 1 .txt file in the directory. 

## Discussions

**1. Testing**

   When the server is live, you can run the unit tests with `python flask_query_api/test/unit_tests.py`. It will copy a `shakespeare.txt` and other test text files into `flask_query_api/api/query/files` for testing, and remove it when finished. Depending on the corpus, abbreviations can be trained (unsupervised) on the corpus and added to the nltk punkt sentence tokenizer. 

**2. API Documentation**

   See `http://localhost:8800/api/`

**3. Data structures**

   The marisa-Trie search have build time of O(N) and lookup time of O(1).

   The sequential search traverse a file line by line with the default python iterator. The search speed is `O(N)` for file size `N`. For `m` consecutive queries, the speed is `O(m*N)`. 

   The text loading for sentence tokenization is paragraph by paragraph (using a modified `read_blankline_block` from nltk). It reads line by line until end of paragraph, then pass to the sentence tokenizer. For large texts, only one paragraph and not the entire document would be loaded into memory. This should be okay for most corpi where a single paragraph can easily fit into memory. If the corpus has unusually large paragraphs, then the code needs to be modified. 
   
   For building a dictionary on a large file (e.g. entire Shakespeare, ~10mb) paging will occur. For future work if had more time, should explore to use the marisa-trie / DAWG stream writer to write to disk and have dict building evoked by app.py start-up initilization, rather than api-call to avoid connection time-out. 
   
**4. Error handling and REST status codes**

Provided using the Flask-RESTPlus framework. 

**5. Deployment instructions**

Deployment for AWS EC2 is provided above. For production enviornment, change `flask_query_api/settings.py` `FLASK_SERVER_NAME` to the production server FQDN name and port, and change `FLASK_DEBUG` to False.


