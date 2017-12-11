import nltk, re, marisa_trie, glob, os
import nltk.tokenize.punkt as pkt
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from flask import jsonify

def query(query_text):

    #sanity check: only 1 txt file should be there
    base_path = "flask_query_api/api/query/files/"
    files = glob.glob(base_path+"*.txt")
    print (files)
    if len(files) != 1:
        print("should only have 1 txt file")
        return "{}"

    #check if dict file already exists
    base=os.path.basename(files[0])
    filename = os.path.splitext(base)[0]
    dict_files = glob.glob(base_path+filename+".dict")

    if not dict_files:
        dictionary = build()
        dictionary.save(base_path+filename+".dict")

    #load dict file
    value_format = ">LLL512s"
    dictionary = marisa_trie.RecordTrie(value_format)
    dictionary.load(base_path+filename+'.dict')

    results = dictionary.get(query_text)
    occurrences = []
    
    while results:
        (lineno, start, end, in_sentence_b) = results.pop(0)
        in_sentence = in_sentence_b.decode(encoding='UTF-8')
        occurrences.append({"line":lineno,"start":start,"end":end,
                            "in_sentence": re.sub(r"\x00","", in_sentence)})

    response = {"query_text": query_text, "number_of_occurrences": len(occurrences), "occurences": occurrences}

    return jsonify(response)
 
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

def build():
    
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
    #Try to add line into dictionary
           
    lineno = 1
    occurrences = []
    keys = []
    values = []

    for para in reader.paras():

        if not para:
            
            lineno += 1
        else:
            #keeping track of the column position of the last sentence in the last paragraph. 
            col_pos = 0
            
           
            for sent in para:
                
                count_line = 0

                sent_no_linebreak = re.sub(r'\n|\r', ' ', sent)
                
                lines = sent.split('\n')

                for line in lines:

                    if count_line != 0:
                        lineno += 1
                        col_pos = len(line)
                        
                        for length in range(1, len(line)+1):
                            for start_pos in range(0, len(line)-length+1):
                                key = line[start_pos:start_pos+length]
                                value = (lineno, start_pos+1, start_pos+length+1,
                                               bytearray(sent_no_linebreak.strip(),'utf-8'))
                                
                                keys.append(key)
                                values.append(value) #(line,start,end,in_sentence)

                    else:
                            
                        for length in range(1, len(line)+1):
                            
                            for start_pos in range(0, len(line)-length+1):
                                
                                key = line[start_pos:start_pos+length]
                                value = (lineno, start_pos+1+col_pos, start_pos+length+1+col_pos,
                                               bytearray(sent_no_linebreak.strip(),'utf-8'))


                                keys.append(key)
                                values.append(value) #(line,start,end,in_sentence)
                            
                        col_pos += len(line)

                    count_line += 1

            lineno += 2
                    
    value_format = ">LLL512s"
    data = zip(keys, values)
    dictionary = marisa_trie.RecordTrie(value_format, data)
    #dictionary = dawg.RecordDAWG(value_format, data)

    return dictionary 
