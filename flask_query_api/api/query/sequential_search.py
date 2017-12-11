import nltk, re
import nltk.tokenize.punkt as pkt
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from flask import jsonify

def query(query_text):

    return jsonify(text_search_sequential(query_text))
 
def my_read_blankline_block(stream):
    s = ''
    while True:
        line = stream.readline()
        # End of file:
        if not line:
            if s: 
                return ([s])
            else: return ([])
       
        #modifying this to not discard empty lines so as to mess up our line count
        else:
            s += line
            if (not line.strip()) and s: 
                return([s]) 

#PlaintextCorpusReader works for titles and subtitles because it treats it as paragraphs
class MyCorpusReader(nltk.corpus.reader.PlaintextCorpusReader):

    """
    Slight modification to the PlaintextCorpusReader so that the paras() 
    doesn't return an already word-tokenized list
    """
    
    def _read_para_block(self, stream):
        paras = []
        for para in self._para_block_reader(stream):
            paras.append(self._sent_tokenizer.tokenize(para))
        return paras

class MyLanguageVars(pkt.PunktLanguageVars):

    _period_context_fmt = r"""
        \S*                          # some word material
        %(SentEndChars)s             # a potential sentence ending
        %(NonWord)s*              #  <-- this is so that \n is not stripped after for example ".]\n"
        \s*                       #  <-- THIS is what I changed
        (?=(?P<after_tok>
            %(NonWord)s              # either other punctuation
            |
            (?P<next_tok>\S+)     #  <-- Normally you would have \s+ here
        ))"""

def text_search_sequential(search_term):
    
    #this custom tokenizer doesn't handle abbrev as well, need to add it:
    my_punkt_param = PunktParameters()
    my_punkt_param.abbrev_types = set(['dr','vs','mr','mrs','prof','inc',
                                       'd.c','a.d', 'b.c', 'r.s.v.p','p.s',
                                       'a.s.a.p','e.t.a','d.i.y','r.i.p','e.g'])

    my_sent_tokenizer = pkt.PunktSentenceTokenizer(lang_vars=MyLanguageVars(), 
                                                   train_text=my_punkt_param)

    reader = MyCorpusReader("flask_query_api/api/query/files/", 
                        ".*\.txt",
                        para_block_reader=my_read_blankline_block,
                        sent_tokenizer=my_sent_tokenizer)

    #the "\n" (or, "%0A") passed from url 
    search_two_lines = re.search(r'\n', search_term)

    lineno = 1
    occurrences = []

    for para in reader.paras():

        if not para:
            lineno += 1
        else:
            #keeping track of the column position of the last sentence in the last paragraph. 
            col_pos = 0 
            
            for sent in para:
                count_line = 0
                
                sent_no_linebreak = re.sub(r'\n|\r', ' ', sent)
                            
                results_sent_list = []
                
                for m in re.finditer(re.escape(search_term), sent):
                    results_sent_list.append({'start': m.start()+1, 'end': m.end()+1, 
                                              'in_sentence': sent_no_linebreak.strip()})
                
                result = None
                if results_sent_list:
                    result = results_sent_list.pop(0)
                
                sent_pos = 0
                lines = sent.split('\n')
                for line in lines:
                    
                    if count_line != 0: 
                        lineno += 1
                        col_pos = len(line) 
                        
                        # use while because may have multiple matches per line
                        while result and (sent_pos + len(line) + count_line > result['start']):
                            result['line'] = lineno
                            result['start'] -= (sent_pos + count_line)
                            result['end'] -= (sent_pos + count_line)
                            
                            if search_two_lines:
                                result['end'] -= (len(line) + 1)
                            
                            occurrences.append(result)
                            if results_sent_list: 
                                result = results_sent_list.pop(0)
                            else: result = None
                        
                        sent_pos += len(line)
                    else: 
                        
                        while result and (len(line) > result['start']): #search found on current line
                            result['line'] = lineno
                            result['start'] += col_pos
                            result['end'] += col_pos
                            
                            if search_two_lines:
                                result['end'] -= (len(line) + 1)
                                
                            occurrences.append(result)
                            if results_sent_list: 
                                result = results_sent_list.pop(0)
                            else: result = None
                        
                        col_pos += len(line) 
                        sent_pos += len(line)
                    
                    count_line += 1
                 
            lineno += 2
            
    response = {"query_text": search_term, "number_of_occurrences": len(occurrences), "occurences": occurrences}
    return response
