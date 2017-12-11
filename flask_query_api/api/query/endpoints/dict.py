import logging

from flask import request, jsonify
from flask_restplus import Resource
from flask_query_api.api.query.dict_search import query
from flask_query_api.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('query_trie', description='Search text file with marisa-trie O(n) build O(1) look-up')

@ns.route('/')
@api.response(403, 'Please enter a search term.')
class EmptyQuery(Resource):

    def get(self):
        return "Please enter a search term.", 403

@ns.route('/<string:query_text>')
@api.response(200, 'OK')
class SequentialQuery(Resource):

    def get(self, query_text):
        """
        Returns search results
        """
        return query(query_text)

