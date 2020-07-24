"""
Group of corpora/nlp tools developed by Connor Bechler

"""

import string
import pathlib
import re
from docxconv import get_docx_text

#Wordlist
pronouns = "i me my we us our own you your they them their it she he her him his what who whom that this those these".split(' ')
pronouns += "which lots lot much some one all many other".split(' ')
freqverbs = "be been being is am was were are had has have do does done doing did go going gone give given come came".split(' ')
freqverbs += "want wanted say said says talked work worked working need needs needed make get see".split(' ')
freqnouns = "things people time years year job jobs".split(' ')
adverbs = "really very well".split(' ')
modals = "should would could can will may must let".split(' ')
funcwords = "if the an a and or as but for so because also only how what why than like".split(' ')
prepwords = "of in out on to by with here there at then when from up where around just over within never before".split(' ')
prepwords += "still upon after away while back into after about".split(' ')
freqadjs = "good more great long".split(' ')
negators = "no not n't".split(' ')
contractions = "i'm she's he's they're who're who's didn't don't doesn't wasn't isn't can't".split(' ')
letters = "a b c d e f g h j k l m n o p q r s t u v w y x z".split(' ')
bizspeak = "organization team".split(' ')
punclist = [x for x in string.punctuation] + ['–'] + ['¶'] + ['§']
whtlist = [x for x in string.whitespace] + ['\n']
common = (pronouns + freqverbs + freqnouns + adverbs + modals + funcwords + prepwords + freqadjs + negators + contractions 
+ letters + bizspeak + punclist + whtlist)

def tokenize(text):
    """Function for tokenizing words from text and returning them as a list
    Currently performs two layers of prefix removal and two layers of suffix removal
    """
    seppunc = string.punctuation + string.whitespace
    #gramtok = "'s 'd 'm".split(" ")
    text = text.replace('\n', ' \n ')
    toks1 = text.split(' ')
    toks2 = []
    toks3 = []
    toks4 = []
    toks5 = []
    #Remove prefixes
    for x in range(len(toks1)):
        tok = toks1[x]
        if tok not in string.whitespace:
            if tok[0] in seppunc:
                toks2.append(tok[0])
                toks2.append(tok[1:])
            else : 
                toks2.append(tok)
        else : 
                toks2.append(tok)
    for x in range(len(toks2)):
        tok = toks2[x]
        if tok not in string.whitespace:
            if tok[0] in seppunc:
                toks3.append(tok[0])
                toks3.append(tok[1:])
            else : 
                toks3.append(tok)
        else : 
                toks3.append(tok)
    #Remove suffixes
    for x in range(len(toks3)):
        tok = toks3[x]
        if tok not in string.whitespace:
            if tok[-1] in seppunc:
                toks4.append(tok[:-1])
                toks4.append(tok[-1])
            else :
                toks4.append(tok)
        else :
                toks4.append(tok)
    for x in range(len(toks4)):
        tok = toks4[x]
        if tok not in string.whitespace:
            if tok[-1] in seppunc and tok[:-1].isalpha():
                toks5.append(tok[:-1])
                toks5.append(tok[-1])
            else :
                toks5.append(tok)
        else :
                toks5.append(tok)
    #Remove blank spaces in list
    toks5 = ' '.join(toks5).split()

    return toks5

def find_and_replace(text, rules):
    """Function for mass find and replace outputting cleaned text files"""
    ruleset = []
    rulines = rules.split('END\n')
    for x in rulines:
        rule = x.split('\t')
        #print(rule)
        if len(rule)>1:
            ruleset.append([rule[0], rule[2]])
    for x in range(len(ruleset)):
        text = text.replace(ruleset[x][0], ruleset[x][1])
    return text

ruleset0 = (
"""What are the top three strengths of\t=>\t**1. What are the top three strengths ofEND
What are the top three areas\t=>\t**2. What are the top three areasEND
What are the top three weaknesses\t=>\t**2. What are the top three weaknessesEND
What are the CEO\t=>\t**3. What are the CEOEND
Please list three ways\t=>\t**4. Please list three waysEND
What are the critical issues\t=>\t**5. What are the critical issuesEND
What does success\t=>\t**6. What does successEND
What one change\t=>\t**7. What one changeEND
Do you have confidence\t=>\t**8. Do you have confidenceEND
Is there anything else\t=>\t**9. Is there anything elseEND
  \t=>\t END
’\t=>\t'END
""")

ruleset1 = (
"""*	=>\t END
0. 	=>	**0. END
\n1. 	=>	\n**1. END
\n2. 	=>	\n**2. END
\n3. 	=>	\n**3. END
\n4. 	=>	\n**4. END
\n5. 	=>	\n**5. END
\n6. 	=>	\n**6. END
\n7. 	=>	\n**7. END
\n8. 	=>	\n**8. END
\n9. \t=>\t\n**9. END
  \t=>\t END
’	=>	'END
""")

def iter_find_replace(directory, rules):
    """Function for iteratively finding and replacing throughout all files within a directory"""
    count = 0
    for path in pathlib.Path(directory).iterdir():
            if path.is_file():
                count +=1
                with open(path, encoding='utf8', errors='replace') as f:
                    text = f.read()
                    newtext = find_and_replace(text, rules)
                #print(str(path))
                with open(str(path)[:-4] + '_cleaned.txt', mode='w', encoding='utf8', errors='replace') as w:
                    w.write(newtext)
    #print('Iterated through', count, 'files!')

def iter_conv_docx(directory, rules):
    """Function for iteratively converting and cleaning all docx files within a directory"""
    textlist = []
    newtexts = []
    non = "interview Interview".split()
    for path in pathlib.Path(directory).iterdir():
            if path.is_file():
                #Locate the interviewee name from file name
                fname = str(path).split('\\')[-1]
                fname = fname[:-5]
                cklst = fname.split(' ')
                name = []
                for x in cklst[2:]:
                    if x.isalpha() and x not in non:
                        if any(c.isupper() for c in x):
                            name.append(x)
                name = ' '.join(name)
                textlist.append((fname, name, get_docx_text(path)))
    for x in textlist:
        newtexts.append('**0. Background\n' + x[1] + '\n' + find_and_replace(x[2], rules))
    return newtexts

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|me|edu)"

def sentence_seg(text):
    """Function for segmenting sentences into a list
    From https://stackoverflow.com/questions/4576077/how-can-i-split-a-text-into-sentences"""
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("¶", "¶<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

if __name__ == "__main__":

    test = 'Within the U.S., there are many unique and powerful traditions. In M.I., 1.2.!'
    

    #with open('C:/users/cbech/desktop/nlp/MEDAInterviewData5.txt', encoding='utf8', errors='replace') as f:
        #test = f.read()
    #print(tokenize(test))

    ruleset2 = "’\t=>\t'END\n"

    #directory = 'C:/users/cbech/desktop/nlp/MEDANewData'
    #iter_find_replace(directory, ruleset1)
