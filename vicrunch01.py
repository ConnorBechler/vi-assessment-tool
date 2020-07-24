"""
Experimental qualitative data parser for VI

"""

#import nltk
#wnl = nltk.WordNetLemmatizer()
from printtools import print_adv, print_data
import spacy
nlp = spacy.load("en_core_web_sm")
#TODO: COREFERENCING MODEL (neuralcoref incompatible, may improvise, maybe abandon)
#TODO: 

pronouns = "i me we us our you your they them their it she he her him his what who whom that".split(" ")
freqverbs = "be been is was were are had has have".split(" ")

class Data:
    """NLP data objects possessing lists of sectioned texts and corresponding spacy nlp docs"""

    def __init__(self, basefilename, num_files=1, num_sections=1, section_char='**'):
        """Initialize data object, import and generate segmented and nlp processed full text"""

        #Set base attributes
        self.basefilename = basefilename
        self.num_files = num_files
        self.section_char = section_char
        self.fullsel = [0, num_sections]
        self.sel = self.fullsel
        #Analysis attributes
        self.conc_window = 10
        self.count_min = 5

        #Initialize data structures
        self.texts_seg = self.import_texts()
        self.texts_merged = self.section_deseg(0, num_sections)
        self.texts_nlp = nlp(self.texts_merged)
        self.working_doc = self.texts_nlp
        self.sec_bounds = self.id_sec_bounds(self.working_doc)

    def up_sel(self, new_sel):
        """Method for updating selection"""
        
        if new_sel != self.sel:
            self.sel = new_sel
            #Check if selection is different than full doc
            if self.sel != self.fullsel:
                section_num = self.sel[0]
                section_end = None
                if self.sel[0] != self.sel[1]:
                    section_end = self.sel[1]
                self.working_doc = nlp(self.section_deseg(section_num, section_end))
            #If not return prepocessed full doc
            else :
                self.working_doc = self.texts_nlp
            self.sec_bounds = self.id_sec_bounds(self.working_doc)
    
    def import_texts(self):
        """Method for importing """
        
        textlist = []
        for x in range(self.num_files):
            with open(self.basefilename + str(x+1) + '.txt', encoding='utf8', errors='replace') as f:
                textlist.append([str(x+1), f.read()])
        segmented_list = []
        for x in range(len(textlist)):
            segmented_list.append(self.section_seg(textlist[x][1], textlist[x][0]))
        return segmented_list

    def section_seg(self, text, textnum):
        """Method for segmenting texts into sections and trimming line breaks"""
        
        #Break into sections
        sections = text.split(self.section_char)
        sections = sections[1:]
        #Trim whitespace
        for s in range(len(sections)):
            mod = sections[s].split('\n')
            sections[s] = ""
            #Embed section headings as non words
            for n in mod:
                if len(n) > 1:
                    if not n[0].isnumeric():
                        sections[s] += n + " "
                    else :
                        #ALT sections[s] += "_".join(n.split(" ")) + " "
                        sections[s] += textnum + '.' + n[:3]
        return sections
    
    def section_deseg(self, section_num, section_end=None):
        """Method for retrieving and combining sections into texts"""

        result = ""
        #Combine all sections of the same number 
        if section_end == None:
            for x in range(len(self.texts_seg)):
                result += self.texts_seg[x][section_num] + '\n'
        #Combine all sections within the same range of numbers
        else:
            for x in range(len(self.texts_seg)):
                for y in self.texts_seg[x][section_num:section_end+1]:
                    result += y + '\n'
        return result

    def id_sec_bounds(self, doc):
        """Method for returning the indices of specific sections"""
        results = []
        for x in range(len(doc)):
            tok = doc[x].text
            if len(tok) > 2:
                if tok[0].isdigit() and tok[1] == '.' and tok[2].isdigit():
                    results.append([doc[x].text, x])
        return results
        
    def return_sec(self, ind):
        """Method for returning which section an idex is within"""
        for v in range(len(self.sec_bounds)-1):
             if ind >= self.sec_bounds[v][1] and ind < self.sec_bounds[v+1][1]:
                 return self.sec_bounds[v][0]

    def count_words(self):
        """Method for counting relevant words within a selection"""
        
        doc = self.working_doc
        results = {}
        target_pos = "ADJ NOUN PROPN VERB".split(" ")
        unwanted = pronouns + freqverbs

        results["Total Selection Tokens:"] = len(doc)
        for x in range(len(doc)):
            token = doc[x]
            if token.pos_ in target_pos and token.text.lower() not in unwanted :
                result = token.text.lower() + ' ' + token.pos_
                for child in token.children:
                    if child.dep_ == "neg":
                        result = "-" + result 
                results[result] = results.get(result, 0) + 1
        results = self.filter_counts(results)
        return results

    def count_chunks(self):
        """Method for counting chunks within a selection"""

        doc = self.working_doc
        results = {}
        count = 0

        for chunk in doc.noun_chunks:
            count += 1
            if chunk.text.lower() not in pronouns:
                result = chunk.text
                results[result] = results.get(result, 0) + 1
        
        results["Total Noun Chunks:"] = count
        return results

    def count_nouns_by_chunks(self):

        doc = self.working_doc
        results = {}

        for chunk in doc.noun_chunks:
            if chunk.text.lower() not in pronouns:
                if chunk.root.text not in list(results):
                    results[chunk.root.text] = [1, [chunk.text]]
                else :
                    results[chunk.root.text][0] += 1
                    results[chunk.root.text][1].append([chunk.text])
        
        results = self.filter_counts(results)
        return results

    def count_conc_noun_chunks(self):

        doc = self.working_doc
        results = {}

        for chunk in doc.noun_chunks:
            if chunk.text.lower() not in pronouns:
                if chunk.root.text not in list(results):
                    results[chunk.root.text] = [1, {chunk.text : []}]
                else :
                    results[chunk.root.text][0] += 1
                    results[chunk.root.text][1][chunk.text] = []
        results = self.filter_counts(results)

        for head in list(results):
            for chunk in results[head][1]:
                results[head][1][chunk].append(self.conc_word(chunk))

        return results

    def filter_counts(self, inpt):
        """Method for removing too low of counts from a count dictionary"""
        
        out = inpt
        keys = list(inpt)
        
        for key in keys:
            if isinstance(out[keys[0]], int) : 
                count = out[key]
            elif isinstance(out[keys[0]][0], int)  : 
                count = out[key][0]
            if count < self.count_min:
                del(out[key])
        return out

    def analyze_target(self, target):
        """Returns all sentences mentioning a target entity in the selection"""

        doc = self.working_doc
        results = []

        #for cluster in doc._.coref_clusters:
            #print(cluster.mentions)

        for sent in doc.sents:
            if (' ' + target.lower() + ' ') in sent.text.lower():
                sec = self.return_sec(sent.start)
                results.append([sec, sent.start, sent.text])
        
        return results
                
    def conc_word(self, words):
        """Method for returning concordances"""
        
        if len(words) > 1:
            wordl = words.split(" ")
            word = wordl[0]
        else :
            word = words
        doc = self.working_doc

        results = []
        negated = False
        if word[0] == '-':
            negated = True
            word = word[1:]

        for x in range(len(doc)):
            token = doc[x] 
            bad = False
            if token.text.lower() == word.lower():
                if word == words:
                    if negated:
                        for child in token.children:
                            if child.dep_ == "neg":
                                results.append(self.conc_line(x))
                    else : results.append(self.conc_line(x))
                else :
                    for y in range(1, len(wordl)):
                        if x+y < len(doc):
                            if doc[x+y].text != wordl[y]:
                                bad = True
                    if not bad:
                        results.append(self.conc_line(x))
                    
        return results

    def conc_line(self, index):
        """Method for returning concordance line"""
        
        doc = self.working_doc
        win = self.conc_window
        lcon = ""
        rcon = ""
        sec = self.return_sec(index)

        for i in range(index-win, index):
            if i >= 0:
                if '\n' not in doc[i].text:
                    lcon += doc[i].text + " "
                else : lcon += '¶ '
            if i+win+1 < len(doc):
                if '\n' not in doc[i+win+1].text:
                    rcon += doc[i+win+1].text + " "
                else : rcon += '¶ '
        return [sec, index, lcon, doc[index].text, rcon]

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

if __name__ == "__main__":

    basefilename = 'MEDAInterviewData'                        
    #test_line = "Dorothy does not understand the organization, articulate a clear vision, or engage effectively with her team or with the staff."
    test = Data(basefilename, 5, 10)
    #test.up_sel([4,4])
    #print(sort_dict(test.count_words()))
    #print(test.conc_word("She"))
    
    #print_data(test.analyze_target("Dorothy"))
    #print_data_better(test.count_nouns_by_chunks())
    
    #print_adv(test.count_conc_noun_chunks(), l1o='', l1e='\n', l2o='\n||', l2e=': ', l3o='', l3e='||\n\n', l5o='\n--', l5e='--\n', mid='8 \n')
    #print_data(test.count_words())
    #print_adv(test.conc_word("the board"), mid='2 \n')
    
    choice = ''
    while choice!='exit':
        bank = test.count_conc_noun_chunks()
        try:
            choice = input('Search noun: ')
            query = bank[choice]
            print_adv(query, l1o='Number: ', l1e='\n', l3o='||', l3e='||\n', mid='6 \n')
        except Exception as e:
            print(e)

    #print_data(test.conc_word("-understand"))