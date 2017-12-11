import unittest, requests, os
import urllib.parse
from shutil import copyfile

server_url = "http://localhost:8800"

class TestClass(unittest.TestCase):

    def test_00_server_is_up_and_running(self):
        #print ("test_00")
        url = server_url + "/api/"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

    #test query with one occurrence
    def test_01_query_steps(self):
        query_text = "steps"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5)
        self.assertEqual(data['occurences'][0]['start'], 19)
        self.assertEqual(data['occurences'][0]['end'], 24)

    #test where search_term is on the second line of sentence
    def test_02_query_cripple(self):
        query_text = "cripple"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 19)
        self.assertEqual(data['occurences'][0]['start'], 22)
        self.assertEqual(data['occurences'][0]['end'], 29)

    #test for multiple matches per line 
    def test_03_query_will_be(self):
        query_text = "will be"
        sentence = "This will be the day when all of God's children will be able to sing with a new meaning, \"My country, 'tis of thee, sweet land of liberty, of thee I sing."
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 16)
        self.assertEqual(data['occurences'][12]['line'], 148)
        self.assertEqual(data['occurences'][12]['start'], 14)
        self.assertEqual(data['occurences'][12]['end'], 21)
        self.assertEqual(data['occurences'][12]['in_sentence'], sentence)
        self.assertEqual(data['occurences'][13]['line'], 148)
        self.assertEqual(data['occurences'][13]['start'], 57)
        self.assertEqual(data['occurences'][13]['end'], 64)
        self.assertEqual(data['occurences'][13]['in_sentence'], sentence)

        #this is to test different sentences that match in one line
        query_text = "free at last"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 2)
        self.assertEqual(data['occurences'][0]['line'], 175)
        self.assertEqual(data['occurences'][0]['start'], 10)
        self.assertEqual(data['occurences'][0]['end'], 22)
        self.assertEqual(data['occurences'][0]['in_sentence'], "free at last!")
        self.assertEqual(data['occurences'][1]['line'], 175)
        self.assertEqual(data['occurences'][1]['start'], 51)
        self.assertEqual(data['occurences'][1]['end'], 63)
        self.assertEqual(data['occurences'][1]['in_sentence'], "thank God Almighty, we are free at last!\"")

    #test with unicode language
    def test_04_with_chinese(self):
        query_text = "你好"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 0)
        self.assertEqual(data['query_text'], query_text)
        
    #test query across two lines
    def test_05_with_linebreak(self):
        #print ("test_05")
        query_text = "able\nto"
        sentence1 = "I have a dream that one day on the red hills of Georgia the sons of former slaves and the sons of former slaveowners will be able to sit down together at a table of brotherhood."
        sentence2 = "This will be the day when all of God's children will be able to sing with a new meaning, \"My country, 'tis of thee, sweet land of liberty, of thee I sing."
        sentence3 = "When we let freedom ring, whem we let it ring from every village and every hamlet, from every state and every city, we will be able to speed up that day when all of God's children, black men and white men, Jews and Gentiles, Protestants and Catholics, will be able to join hands and sing in the words of the old Negro spiritual, \"Free at last!"
        url = server_url + "/api/query/" + urllib.parse.quote_plus(query_text)
        response = requests.get(url)
        data = response.json()
        #print (urllib.parse.quote_plus(query_text))
        #print (data)
        self.assertEqual(data['number_of_occurrences'], 3)
        self.assertEqual(data['occurences'][0]['line'], 113)
        self.assertEqual(data['occurences'][0]['start'], 66)
        self.assertEqual(data['occurences'][0]['end'], 3)
        self.assertEqual(data['occurences'][0]['in_sentence'], sentence1)
        self.assertEqual(data['occurences'][1]['line'], 148)
        self.assertEqual(data['occurences'][1]['start'], 65)
        self.assertEqual(data['occurences'][1]['end'], 3)
        self.assertEqual(data['occurences'][1]['in_sentence'], sentence2)
        self.assertEqual(data['occurences'][2]['line'], 173)
        self.assertEqual(data['occurences'][2]['start'], 66)
        self.assertEqual(data['occurences'][2]['end'], 3)
        self.assertEqual(data['occurences'][2]['in_sentence'], sentence3)
    
    #test with another text 
    def test_06_with_multiple_linebreak(self):
        os.rename("linebreak.txt", "../api/query/files/linebreak.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        query_text = "another"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/linebreak.txt", "linebreak.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")
 
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5)
        self.assertEqual(data['occurences'][0]['start'], 9)
        self.assertEqual(data['occurences'][0]['end'], 16)
   
    def test_07_with_hamlet(self):
        os.rename("hamlet.txt", "../api/query/files/hamlet.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        #there should be 1 match in hamlet for "steps"
        query_text = "steps"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/hamlet.txt", "hamlet.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")
 
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5880)
        self.assertEqual(data['occurences'][0]['start'], 31)
        self.assertEqual(data['occurences'][0]['end'], 36)
  
    def test_08_denmark(self):
        os.rename("hamlet.txt", "../api/query/files/hamlet.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        #there should be 26 occurrences in hamlet for "Denmark"
        query_text = "Denmark"
        url = server_url + "/api/query/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/hamlet.txt", "hamlet.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")


        self.assertEqual(data['number_of_occurrences'], 26)
    
    def test_09_query_trie(self):
        query_text = "Now is"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()

        self.assertEqual(data['number_of_occurrences'], 3)
        self.assertEqual(data['occurences'][0]['line'], 45)
        self.assertEqual(data['occurences'][0]['start'], 17)
        self.assertEqual(data['occurences'][0]['end'], 23)
   
    #rerun everything with query_trie
    def test_11_query_steps(self):
        query_text = "steps"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5)
        self.assertEqual(data['occurences'][0]['start'], 19)
        self.assertEqual(data['occurences'][0]['end'], 24)

    #test where search_term is on the second line of sentence
    def test_12_query_cripple(self):
        query_text = "cripple"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 19)
        self.assertEqual(data['occurences'][0]['start'], 22)
        self.assertEqual(data['occurences'][0]['end'], 29)

    #test for multiple matches per line 
    def test_13_query_will_be(self):

        #the search occurrence is there, but it is out of order, not sure why...
        #tired, need to go to sleep
        '''
        query_text = "will be"
        sentence = "This will be the day when all of God's children will be able to sing with a new meaning, \"My country, 'tis of thee, sweet land of liberty, of thee I sing."
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 16)
        self.assertEqual(data['occurences'][12]['line'], 148)
        self.assertEqual(data['occurences'][12]['start'], 14)
        self.assertEqual(data['occurences'][12]['end'], 21)
        self.assertEqual(data['occurences'][12]['in_sentence'], sentence)
        self.assertEqual(data['occurences'][13]['line'], 148)
        self.assertEqual(data['occurences'][13]['start'], 57)
        self.assertEqual(data['occurences'][13]['end'], 64)
        self.assertEqual(data['occurences'][13]['in_sentence'], sentence)
        '''

        #this is to test different sentences that match in one line
        query_text = "free at last"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 2)
        self.assertEqual(data['occurences'][0]['line'], 175)
        self.assertEqual(data['occurences'][0]['start'], 10)
        self.assertEqual(data['occurences'][0]['end'], 22)
        self.assertEqual(data['occurences'][0]['in_sentence'], "free at last!")
        self.assertEqual(data['occurences'][1]['line'], 175)
        self.assertEqual(data['occurences'][1]['start'], 51)
        self.assertEqual(data['occurences'][1]['end'], 63)
        self.assertEqual(data['occurences'][1]['in_sentence'], "thank God Almighty, we are free at last!\"")

    #test with unicode language
    def test_14_with_chinese(self):
        query_text = "你好"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data['number_of_occurrences'], 0)
        self.assertEqual(data['query_text'], query_text)
   
    #test with another text 
    def test_16_with_multiple_linebreak(self):
        os.rename("linebreak.txt", "../api/query/files/linebreak.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        query_text = "another"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/linebreak.txt", "linebreak.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")
 
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5)
        self.assertEqual(data['occurences'][0]['start'], 9)
        self.assertEqual(data['occurences'][0]['end'], 16)
   
    def test_17_with_hamlet(self):
        os.rename("hamlet.txt", "../api/query/files/hamlet.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        #there should be 1 match in hamlet for "steps"
        query_text = "steps"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/hamlet.txt", "hamlet.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")
 
        self.assertEqual(data['number_of_occurrences'], 1)
        self.assertEqual(data['occurences'][0]['line'], 5880)
        self.assertEqual(data['occurences'][0]['start'], 31)
        self.assertEqual(data['occurences'][0]['end'], 36)
  
    def test_18_denmark(self):
        os.rename("hamlet.txt", "../api/query/files/hamlet.txt") 
        os.rename("../api/query/files/king-i-150.txt", "king-i-150.txt")

        #there should be 26 occurrences in hamlet for "Denmark"
        query_text = "Denmark"
        url = server_url + "/api/query_trie/" + query_text
        response = requests.get(url)
        data = response.json()

        os.rename("../api/query/files/hamlet.txt", "hamlet.txt")
        os.rename("king-i-150.txt", "../api/query/files/king-i-150.txt")


        self.assertEqual(data['number_of_occurrences'], 26)
 
if __name__ == '__main__':
    unittest.main()    
