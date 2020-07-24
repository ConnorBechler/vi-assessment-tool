"""
Experimental qualitative data parser for VI
"""


from corptools import tokenize, common, sentence_seg
from printtools import print_adv, print_data
import string
import pathlib 

class Data:
    """NLP data objects possessing lists of sectioned texts and corresponding spacy nlp docs"""

    def __init__(self, basedirectory, num_sections=1, section_char='**', preimported=None):
        """Initialize data object, import and generate segmented and tokenized full text"""

        #Set base attributes
        self.basedirectory = basedirectory
        self.section_char = section_char
        self.fullsel = [0, num_sections]
        self.sel = self.fullsel
        self.preimported = preimported
        #Analysis attributes
        self.conc_win = 50
        self.count_min = 5
        self.unwanted = common
        self.text_names = {}

        #Initialize data structures
        self.texts_seg = self.import_texts()
        self.texts_merged = self.section_deseg(0, num_sections)
        self.texts_nlp = tokenize(self.texts_merged)
        self.working_text = self.texts_merged
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
                self.working_text = self.section_deseg(section_num, section_end)
                self.working_doc = tokenize(self.working_text)
            #If not return prepocessed full doc
            else :
                self.working_text = self.texts_merged
                self.working_doc = self.texts_nlp
            self.sec_bounds = self.id_sec_bounds(self.working_doc)
    
    def import_texts_OLD(self):
        """LEGACY Method for importing all texts with the same base file name"""
        
        textlist = []
        for x in range(self.num_files):
            with open(self.basedirectory + str(x+1) + '.txt', encoding='utf8', errors='replace') as f:
                textlist.append([str(x+1), f.read()])
        segmented_list = []
        for x in range(len(textlist)):
            segmented_list.append(self.section_seg(textlist[x][1], textlist[x][0]))
        return segmented_list
    
    def import_texts(self):
        """Method for importing all texts in a directory"""
        textlist = []
        count = 0
        if self.preimported == None:
            for path in pathlib.Path(self.basedirectory).iterdir():
                if path.is_file():
                    count += 1
                    with open(path, encoding='utf8', errors='replace') as f:
                        textlist.append([str(count), f.read()])
        else:
            for x in range(len(self.preimported)):
                count += 1
                textlist.append([str(count), self.preimported[x]])
        segmented_list = []
        for x in range(len(textlist)):
            segmented_list.append(self.section_seg(textlist[x][1], textlist[x][0]))
        self.num_files = count
        return segmented_list

    def section_seg(self, text, textnum):
        """Method for segmenting texts into sections and trimming line breaks"""
        #Break into sections
        sections = text.split(self.section_char)
        sections = sections[1:]
        textname = (sections[0].split('\n')[1])
        textname = ' ' + '_'.join(textname.split(' ')) + ' '
        self.unwanted += [textname[1:-1].lower()]
        self.text_names[textname[1:-1]] = textnum
        #If specified number of sections are missing, create missing sections
        if len(sections) < self.fullsel[1] + 1:
            for s in range(self.fullsel[1]+1):
                if s < len(sections):
                    if s < int(sections[s][0]):
                        sections.insert(s, str(s) + '. ')
                else:
                    sections.append(str(int(sections[-1][0])+1) + '. ')
        #Trim whitespace
        for s in range(len(sections)):
            sections[s] = sections[s].replace('\n', ' ¶\n')
            mod = sections[s].split('\n')
            #name = " _" + "_".join(mod[3].split(" "))
            sections[s] = ""
            #Embed section headings as non words
            for n in mod:
                if len(n) > 1:
                    if n[0].isnumeric() and n[1] == '.' :
                        #ALT sections[s] += "_".join(n.split(" ")) + " "
                        sections[s] += '§ ' + textnum + '.' + n[:3] + textname.upper()
                        #DEBUG print(sections[s])
                    else :
                        sections[s] += n + " "
        return sections
    
    def section_deseg(self, section_num, section_end=None):
        """Method for retrieving and combining sections into texts"""
        result = ""
        #Combine all sections of the same number 
        if section_end == None:
            for x in range(len(self.texts_seg)):
                if len(self.texts_seg[x]) > section_num:
                    #Screen out non-responses
                    if len(self.texts_seg[x][section_num]) > 30 :
                        result += self.texts_seg[x][section_num] + '\n'
                    #DEBUG else: print(self.texts_seg[x][section_num], "too short to be included")
        #Combine all sections within the same range of numbers
        else:
            for x in range(len(self.texts_seg)):
                if len(self.texts_seg[x]) > section_end:
                    for y in self.texts_seg[x][section_num:section_end+1]:
                        #Screen out non-responses
                        if len(y) > 30 :
                            result += y + '\n'
                        #DEBUG else: print(y, "too short to be included")
                else:
                    for y in self.texts_seg[x][section_num:]:
                        #Screen out non-responses
                        if len(y) > 30 :
                            result += y + '\n'
                        #DEBUG else: print(y, "too short to be included")
        return result

    def id_sec_bounds(self, doc):
        """Method for returning the indices of specific sections"""
        results = []
        for x in range(len(doc)):
            tok = doc[x]
            if len(tok) > 2:
                if doc[x-1] == '§':
                    if tok[0].isdigit() and tok[1] == '.' and tok[2].isdigit():
                        results.append([doc[x], x])
                    elif tok[:2].isdigit() and tok[2] == '.' and tok[3].isdigit():
                        results.append([doc[x], x])
        return results
        
    def return_sec(self, ind):
        """Method for returning which section an idex is within"""
        for v in range(len(self.sec_bounds)-1):
             if ind >= self.sec_bounds[v][1] and ind < self.sec_bounds[v+1][1]:
                 return self.sec_bounds[v][0]
        if ind >= self.sec_bounds[len(self.sec_bounds)-1][1] :
            return self.sec_bounds[len(self.sec_bounds)-1][0]
                
    def conc_word(self, words):
        """Method for returning concordances"""
        wordl = tokenize(words)
        word = wordl[0]
        doc = self.working_doc

        results = []

        for x in range(len(doc)):
            token = doc[x] 
            bad = False
            if token.lower() == word.lower():
                if word == words:
                    results.append(self.conc_line(x))
                else :
                    for y in range(1, len(wordl)):
                        if x+y < len(doc):
                            if doc[x+y] != wordl[y]:
                                bad = True
                    if not bad:
                        results.append(self.conc_line(x))
                    
        return results

    def conc_line(self, index):
        """Method for returning concordance line"""
        doc = self.working_doc
        char = self.conc_win
        win = char//5
        lcon = ""
        rcon = ""
        sec = self.return_sec(index)

        for i in range(index-win, index):
            if i >= 0:
                if '\n' not in doc[i]:
                    lcon += doc[i] + " "
                else : lcon += '¶'
            if i+win+1 < len(doc):
                if '\n' not in doc[i+win+1]:
                    rcon += doc[i+win+1] + " "
                else : rcon += '¶'
        if len(lcon) > char:
            lcon = lcon[-char:]
        if len(rcon) > char:
            rcon = rcon[:char+1] 
        return [sec, index, lcon, doc[index], rcon]

    def sent_word(self, words):
        """Method for returning all sentences including the specified words"""
        wordl = tokenize(words)
        word = wordl[0]
        text = self.working_text
        results = []
        bad = False

        sents = sentence_seg(text)
        for sent in sents:
            if word.lower() in tokenize(sent.lower()):
                #Find section for each sentence
                sent_toks = tokenize(sent)
                conc = self.conc_word(' '.join(sent_toks[:6]))
                if len(conc) > 0:
                    sec = conc[0][0]
                    ind = conc[0][1]
                else:
                    sec = 'Unknown'
                    ind = 'N/A'
                #Append results if sentence contains search words
                if word == words:
                    results.append([sec, ind, sent])
                else:
                    for y in range(1, len(wordl)):
                        if wordl[y].lower() not in sent.lower():
                            bad=True
                    if not bad:
                        results.append([sec, ind, sent])
        return results

    def par_word(self, words):
        """Method for returning all paragraphs including the specified words"""
        wordl = tokenize(words)
        word = wordl[0]
        text = self.working_text
        results = []
        bad = False

        pars = text.split("¶")
        for par in pars:
            if word.lower() in tokenize(par.lower()):
                #Find section for each sentence
                par_toks = tokenize(par)
                conc = self.conc_word(' '.join(par_toks[:6]))
                if len(conc) > 0:
                    sec = conc[0][0]
                    ind = conc[0][1]
                else:
                    sec = 'Unknown'
                    ind = 'N/A'
                #Append results if sentence contains search words
                if word == words:
                    results.append([sec, ind, par])
                else:
                    for y in range(1, len(wordl)):
                        if wordl[y].lower() not in par.lower():
                            bad=True
                    if not bad:
                        results.append([sec, ind, par])
        return results

    def count_words(self):
        """Method for counting and returning unique words in a selection"""

        doc = self.working_doc
        results = {}
        results["# of Tokens"] = len(doc)
        for x in range(len(doc)):
            token = doc[x]
            if token.lower() not in self.unwanted :
                result = token.lower()
                results[result] = results.get(result, 0) + 1
        results = self.filter_counts(results)
        results['# of Results'] = len(results) - 1
        return results

    def count_words_by_sec(self):
        """Method for counting and returning words by the number of sections in which each word occurs"""
        
        doc = self.working_doc
        results = {}
        counted = {}
        results["# of Tokens"] = len(doc)
        for x in range(len(doc)):
            token = doc[x]
            if token.lower() not in self.unwanted :
                result = token.lower()
                sec = self.return_sec(x)
                if result != sec:
                    if result in counted:
                        if sec not in counted[result]:
                            results[result] = results.get(result, 0) + 1
                            counted[result].append(sec)
                    else:
                        results[result] = results.get(result, 0) + 1
                        counted[result] = [sec]
        results = self.filter_counts(results)
        results['# of Results'] = len(results) - 1
        return results

    def count_words_by_both(self, sort=0):
        """Method for counting words by both total and person, then sorting based on user input"""
        doc = self.working_doc
        results = {}
        counted = {}
        #results['# of Tokens'] = [len(doc), len(doc)]
        
        if sort == 0:
            a = 0
            b = 1
        else:
            a = 1
            b = 0
        
        for x in range(len(doc)):
            token = doc[x]
            if token.lower() not in self.unwanted :
                result = token.lower()
                sec = self.return_sec(x)
                per = sec.split('.')[0]
                if result != sec:
                    if result in counted:
                        if per not in counted[result]:
                            results[result][a] += 1
                            results[result][b] += 1
                            counted[result].append(per)
                        else :
                            results[result][a] += 1
                    else :
                        results[result] = [1, 1]
                        counted[result] = [per]
        results = self.filter_counts(results)
        #results['# of Results'] = [len(results) - 1, len(results) - 1]
        return results

    def count_conc_words(self):
        """Method for counting and returning all unique words in a selection and their concordances"""

        doc = self.working_doc
        results = {}

        for x in range(len(doc)):
            token = doc[x]
            if token.lower() not in self.unwanted :
                if token.lower() not in list(results):
                    results[token.lower()] = [1, []] 
                else :
                    results[token.lower()][0] += 1  
        results = self.filter_counts(results)

        for word in list(results):
            results[word][1].append(self.conc_word(word))

        return results

    def filter_counts(self, inpt):
        """Method for removing too low of counts from a count dictionary"""
        
        out = inpt
        if '' in out:
            del(out[''])
        keys = list(inpt)
        #print(keys)
        #print(inpt)
        for key in keys:
            if isinstance(out[key], int) : 
                count = out[key]
            elif isinstance(out[key][0], int)  : 
                count = out[key][0]
            if count < self.count_min:
                del(out[key])
        return out

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Main App Loop/Testing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

if __name__ == "__main__":

    basedirectory = 'MEDAData'                        
    #test_line = "Dorothy does not understand the organization, articulate a clear vision, or engage effectively with her team or with the staff."
    test = Data(basedirectory, 10)
    #test.up_sel([0,10])
    
    #print_adv(test.conc_word("the board"), mid='2 \n 3 \t')
    #print(print_adv(test.count_words(), mid='2 \t', col=15))
    #print(print_adv(test.count_conc_words(), l2o='||', l2e=': ', l3e='||\n', mid='2 \n 6 \n'))
    
    choice = ''
    bank = test.count_words()
    while choice!='exit':
        try:
            choice = input('Search: ')
            query = bank[choice.lower()]
            print(print_adv(query, l1o='Lines: ', l1e='\n', mid='4 \n'))
        except Exception as e:
            print(e)
                 