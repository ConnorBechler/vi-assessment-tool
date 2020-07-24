"""
GUI practice for VI assessment tool

Base drawn from
http://zetcode.com/tkinter/dialogs/
Other help from
https://www.delftstack.com/tutorial/tkinter-tutorial/tkinter-combobox/
https://stackoverflow.com/questions/11295917/how-to-select-a-directory-and-store-the-location-using-tkinter-in-python
https://tkdocs.com/tutorial/complex.html
https://stackoverflow.com/questions/18906047/how-to-update-values-to-the-listbox-under-combobox-in-ttk-python33
"""

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Notebook, Combobox
from vicrunch01B import Data
from printtools import format_conc_lines, print_adv, conv_dict, sort_dict
from corptools import iter_find_replace, iter_conv_docx, ruleset0, ruleset1
import math

class App(Frame):

    def __init__(self, parent):
        """Initializes the app"""

        Frame.__init__(self, parent)   

        self.parent = parent    
        self.data = None
        self.selection = [0]    
        self.secs = IntVar()
        self.conc_win = IntVar()
        self.conc_win.set(50)
        self.count_min = IntVar()
        self.count_min.set(5)
        self.canwidth=500
        self.canheight=500
        self.rules = None
        self.initUI()

    def initUI(self):
        """Initializes the GUI"""

        self.parent.title("Assessment Tool")
        self.pack(fill=BOTH, expand=1)
        #self.centerWindow()

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        self.parent.option_add('*tearOff', False)

        file_menu = Menu(menubar)
        menubar.add_cascade(label='Files', menu=file_menu)
        file_menu.add_command(label="Import docx", command=self.getRulesImport)
        file_menu.add_command(label="Clean txt", command=self.getRulesClean)
        file_menu.add_command(label="Open txt", command=self.getSecs)
        file_menu.add_command(label="Overview", command=self.displayOverview)
        file_menu.add_command(label="Help", command=self.disphelp)
        file_menu.add_command(label="Exit", command=self.onExit)
        
        #Main Screen Setup
        main = Notebook(self.parent)
        
        #Selection Display
        displaygroup = LabelFrame(main, text="Current Selection", padx=5, pady=5)
        displaygroup.pack(padx=10, pady=10)
        
        selectscroll = Scrollbar(displaygroup)
        selectscroll.pack(side=RIGHT, fill=Y)
        
        self.slctxt = Text(displaygroup, state='disabled', yscrollcommand=selectscroll.set, width=130, height=34)
        self.slctxt.pack()

        selectscroll.configure(command = self.slctxt.yview)

        #Search Window
        searchgroup = LabelFrame(main, text="Search Results", padx=5, pady=5)
        searchgroup.pack(padx=10, pady=10)
        
        searchscroll = Scrollbar(searchgroup)
        searchscroll.pack(side=RIGHT, fill=Y)
        
        self.context = Text(searchgroup, state='disabled', yscrollcommand=searchscroll.set, width=130)
        self.context.pack()
        searchscroll.configure(command=self.context.yview)
        
        #   Search form
        searchprm = LabelFrame(searchgroup, padx=5, pady=0, bd=0)
        searchprm.pack(side=LEFT)
        
        srchbox = LabelFrame(searchprm, bd=0)
        srchbox.grid(row=0, column=0, columnspan=2)
        self.search = StringVar()
        search_form = Entry(srchbox, textvariable=self.search, width=30)
        search_form.pack(side=LEFT)
        search_button = Button(srchbox, text="Search", command=self.search_comm)
        search_button.pack(side=LEFT)
        
        #   Search type
        srchtypgrp = LabelFrame(searchprm, text='Type of Search')
        srchtypgrp.grid(row=1, column=0)
        self.typesearch = IntVar()
        self.typesearch.set(1)
        conc_type = Radiobutton(srchtypgrp, text="Concordance", value=1, variable=self.typesearch)
        conc_type.pack(anchor='nw')
        sent_type = Radiobutton(srchtypgrp, text="Sentence", value=2, variable=self.typesearch)
        sent_type.pack(anchor='w')
        par_type = Radiobutton(srchtypgrp, text="Paragraph", value=3, variable=self.typesearch)
        par_type.pack(anchor='sw')
        
        #   Conc settings
        concsettings = LabelFrame(searchprm, text="Concordance Settings")
        concsettings.grid(row=1, column=1)
        charwin_label = Label(concsettings, text="Character window: ", pady=5)
        charwin_label.grid(row=0, column=0)
        self.charwin_entry = Entry(concsettings, textvariable=self.conc_win, width=4)
        self.charwin_entry.grid(row=0, column=1)

        #Count Window
        countgroup = LabelFrame(main, text="Count Results", padx=5, pady=5)
        countgroup.pack(padx=10, pady=10)
        
        #   Left frame
        countleft = LabelFrame(countgroup, padx=5, pady=5)
        countleft.pack(side=LEFT)
        
        countscroll = Scrollbar(countleft)
        countscroll.pack(side=RIGHT, fill=Y)
        countlabels = LabelFrame(countleft)
        countlabels.pack(anchor='nw')
        
        labeltxt = '{word:<45}{ctot:<20}{csec:<20}'
        wordlabel = Label(countlabels, text=labeltxt.format(word='Words', ctot='Total #', csec='# of People'))
        wordlabel.pack(side=LEFT)
        
        self.counttxt = Text(countleft, width=40, state='disabled', yscrollcommand=countscroll.set)
        self.counttxt.pack(anchor='nw')
        countscroll.configure(command=self.counttxt.yview)

        #       Count button
        countbutton = Button(countleft, text="Count", command=self.count_comm)
        countbutton.pack(anchor='w')

        #       Count minimum
        self.countmin_entry = Entry(countleft, textvariable=self.count_min, width=4)
        self.countmin_entry.pack(anchor='ne', side=RIGHT)
        countmin_label = Label(countleft, text="Minimum word count: ")
        countmin_label.pack(anchor='ne', side=RIGHT)

        #       Count sorting
        sortcntgrp = LabelFrame(countleft, text="Sort By:")
        sortcntgrp.pack(anchor='sw')
        self.typecount = IntVar()
        self.typecount.set(1)
        conc_type = Radiobutton(sortcntgrp, text="Total occurence count", value=1, variable=self.typecount)
        conc_type.pack(anchor='sw')
        sent_type = Radiobutton(sortcntgrp, text="Use by people", value=2, variable=self.typecount)
        sent_type.pack(anchor='sw')

        #   Right frame
        countright = LabelFrame(countgroup, text="Word Map", padx=5, pady=5, width=500, height=500)
        countright.pack(side=LEFT)

        countscrolly2 = Scrollbar(countright, orient=VERTICAL)
        countscrolly2.pack(side=RIGHT, fill=Y)
        countscrollx2 = Scrollbar(countright, orient=HORIZONTAL)
        countscrollx2.pack(side=BOTTOM, fill=X)

        self.canvas = Canvas(countright, width=self.canwidth, background='white',
        height=self.canheight, yscrollcommand=countscrolly2.set, xscrollcommand=countscrollx2.set)
        self.canvas.pack()
        self.canvas.config(scrollregion=(0,0, self.canheight, self.canwidth))

        countscrolly2.configure(command=self.canvas.yview)
        countscrollx2.configure(command=self.canvas.xview)

        #Finish initializing main notebook
        main.add(displaygroup, text="Selection")
        main.add(searchgroup, text="Search")
        main.add(countgroup, text="Count")
        main.pack()

        #Selection settings/bottom
        select_group = LabelFrame(self.parent, text="Selection", padx=5, pady=5)
        select_group.pack(padx=10, pady=10, side=LEFT)
        
        self.selsetting = IntVar()
        self.selsetting.set(2)

        self.selsingle = Radiobutton(select_group, text="Single Section", value=1, variable=self.selsetting, command=self.selsectype)
        self.selsingle.pack(side=LEFT)
        self.selrange = Radiobutton(select_group, text="Section Range", value=2, variable=self.selsetting, command=self.selsectype)
        self.selrange.pack(side=LEFT)
        self.sellow = IntVar()
        self.selhi = IntVar()
        self.sellow_form = Combobox(select_group, values=self.selection, textvariable=self.sellow, width=4)
        self.sellow_form.pack(side=LEFT)
        self.selhi_form = Combobox(select_group, values=self.selection, textvariable=self.selhi, width=4)
        self.selhi_form.pack(side=LEFT)

        updt_slct_button = Button(select_group, text="Update Selection", command=self.update_selection)
        updt_slct_button.pack()
    
    def centerWindow(self, w=1000, h=700):
        """Method for centering window on the screen
        From: http://zetcode.com/tkinter/introduction/
        """

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def selsectype(self):
        """Method for switching between single selection and ranged selection"""
        choice = self.selsetting.get()
        if choice ==1 :
            self.selhi_form.configure(state='disabled')
            self.update_selection()
        if choice ==2 :
            self.selhi_form.configure(state='normal')
            self.update_selection()
    
    def getSecs(self):
        """Method for retrieving sections"""
        self.popup = Tk()
        self.popup.wm_title("User Input")
        
        self.popup.geometry('%dx%d+%d+%d' % (300, 100, 350, 350))

        pop_lab = Label(self.popup, text="How many sections are in the documents?")
        pop_lab.pack(side='top')
        self.pop_entry = Entry(self.popup, textvariable=self.secs)
        self.pop_entry.pack()
        q_but = Button(self.popup, text="Enter", command=self.onOpen)
        q_but.pack()

    def onOpen(self):
        """Method for loading data from a directory"""
        self.secs.set(self.pop_entry.get())
        self.selection = [x for x in range(self.secs.get()+1)]
        self.sellow_form['values'] = self.selection
        self.selhi_form['values'] = self.selection
        self.selhi_form.set(self.selection[-1])
        self.popup.destroy()
        dlg = filedialog.askdirectory()
        
        if dlg != '':
            #text = self.readFile(fl)
            #self.txt.insert(END, text)
            self.data = Data(dlg, self.secs.get())
            self.update_txt(self.slctxt, self.data.texts_merged)
    
    def getRulesClean(self):
        """Popup rules display for user editing/approval"""
        self.ruleswin = Tk()
        self.ruleswin.wm_title("Clean Text Docs")
        ruleslabel = Label(self.ruleswin, text="Current Cleaning Rules:")
        ruleslabel.pack()
        self.rulestxt = Text(self.ruleswin)
        self.rulestxt.pack()
        self.rulestxt.insert(END, ruleset1)
        okbutton = Button(self.ruleswin, text="OK", command=self.onClean)
        okbutton.pack()
    
    def onClean(self):
        """Method for loading files to be cleaned from a directory"""
        self.rules = self.rulestxt.get(1.0, END)
        self.ruleswin.destroy()
        dlg = filedialog.askdirectory()
        
        if dlg != '':
            iter_find_replace(dlg, self.rules)
    
    def getRulesImport(self):
        """Method for showing import rules and getting number of sections for import"""
        self.ruleswin = Tk()
        self.ruleswin.wm_title("Import Word Docs")
        ruleslabel = Label(self.ruleswin, text="Current Import Rules:")
        ruleslabel.pack()
        self.rulestxt = Text(self.ruleswin)
        self.rulestxt.pack()
        self.rulestxt.insert(END, ruleset0)
        sel_lab = Label(self.ruleswin, text="How many sections are in the documents?")
        sel_lab.pack()
        self.pop_entry = Entry(self.ruleswin, textvariable=self.secs)
        self.pop_entry.pack()
        okbutton = Button(self.ruleswin, text="OK", command=self.importDocs)
        okbutton.pack()
    
    def importDocs(self):
        """Method for importing docx files"""
        self.rules = self.rulestxt.get(1.0, END)
        self.secs.set(self.pop_entry.get())
        self.selection = [x for x in range(self.secs.get()+1)]
        self.sellow_form['values'] = self.selection
        self.selhi_form['values'] = self.selection
        self.selhi_form.set(self.selection[-1])
        self.ruleswin.destroy()
        dlg = filedialog.askdirectory()

        if dlg !='':
            textlist = iter_conv_docx(dlg, ruleset0)
            self.data = Data(dlg, self.secs.get(), preimported=textlist)
            self.update_txt(self.slctxt, self.data.texts_merged)

    def onExit(self):
        """Command for exiting the program"""
        self.quit()

    def displayOverview(self):
        """Command for opening an overview window"""
        overview = Tk()
        overview.wm_title("Overview")
        #overview.geometry('%dx%d+%d+%d' % (300, 100, 350, 350))
        names= list(self.data.text_names)
        disclabel = Label(overview, text="This directory includes " + str(self.data.num_files) + " interviews:")
        disclabel.pack()
        disc = Text(overview, width=22)
        disc.pack()
        info = ''
        for x in range(len(names)):
            info += str(x+1) + '. ' + ' '.join(names[x].split('_'))
            if x != len(names)-1: info += '\n'
        disc.insert(END, info)
        disc.configure(state='disabled')
        exbutton = Button(overview, text="Exit", command=overview.destroy)
        exbutton.pack()

    def readFile(self, filename):

        f = open(filename, "r")
        text = f.read()
        return text

    def update_selection(self):
        """Simple method for updating selection"""
        if self.data == None:
            self.disp_msg("Error: No dataset opened")
        else:
            newl = self.sellow.get()
            if self.selsetting.get() == 2:
                newh = self.selhi.get()
            else :
                newh = newl
            if newl <= newh:
                self.data.up_sel([newl, newh])
                self.update_txt(self.slctxt, self.data.working_text)
            else:
                self.disp_msg("Error: Selection invalid, not updated")

    def update_settings(self):
        if self.data == None:
            self.disp_msg("Error: No dataset opened")
        else:
            self.update_selection()
            self.data.conc_win = self.conc_win.get()
            self.data.count_min = self.count_min.get()

    def search_comm(self):
        """Search command handler"""
        if self.data != None:
            self.update_settings()
            if self.typesearch.get() == 1:
                words = self.search.get()
                parsed = words.split(' ')
                if parsed[0].isdigit():
                    conclines = [self.data.conc_line(int(parsed[0]))]
                else:
                    conclines = self.data.conc_word(words)
                output = format_conc_lines(conclines)
            elif self.typesearch.get() == 2:
                words = self.search.get()
                sents = self.data.sent_word(words)
                output = print_adv(sents, mid='2 \n')
            elif self.typesearch.get() == 3:
                words = self.search.get()
                pars = self.data.par_word(words)
                output = print_adv(pars, mid='2 \n')
            self.update_txt(self.context, output)
        else:
            self.disp_msg("Error: No dataset opened")

    def count_comm(self):
        """Simple count command"""
        if self.data == None:
            self.disp_msg("Error: No dataset opened")
        else:
            self.update_settings()
            row = '{word:<20}{ctot:<10}{csec:<10}'
            if self.typecount.get() == 1:
                countdata = self.data.count_words_by_both(sort=0)
                words = [x[0] for x in sort_dict(countdata)]
                counttot = [countdata[x][0] for x in words]
                countsec = [countdata[x][1] for x in words]
                self.word_map(words, counttot)
            else :
                countdata = self.data.count_words_by_both(sort=1)
                words = [x[0] for x in sort_dict(countdata)]
                counttot = [countdata[x][1] for x in words]
                countsec = [countdata[x][0] for x in words]
                self.word_map(words, countsec)
            self.counttxt.configure(state='normal')
            self.counttxt.delete(1.0, END)
            for x in range(len(words)):
                output = row.format(word=words[x], ctot=counttot[x], csec=countsec[x])
                self.counttxt.insert(END, output + '\n')
            self.counttxt.configure(state='disabled')

    def update_txt(self, txt, update):
        """Simple method for updating a disabled text field, replacing its current contents with new stuff"""
        txt.configure(state='normal')
        txt.delete(1.0, END)
        txt.insert(END, update)
        txt.configure(state='disabled')

    def word_map(self, words, counts):
        """Method for rendering word map onto canvas"""
        cv = self.canvas
        total = len(words)
        mx_ds = 25
        spc = 90
        if total > 1:
            x = -30
            y = 60
            cv.delete('all')
            mx = int(counts[0])
            if total < mx_ds:
                mn = int(counts[total-1])
            else:
                mn = int(counts[mx_ds-1])
            for j in range(total):
                radius = scale_range(int(counts[j]), mn, mx, 10, 40)
                if x+spc > self.canwidth:
                    x = spc-30
                    y += spc
                else:
                    x += spc
                if y > self.canheight:
                    break
                cv.create_oval(x-radius, y-radius, x+radius, y+radius)
                cv.create_text((x,y), text=words[j])

    def word_map_test1(self, words, counts):
        """Method for rendering word map onto canvas"""
        cv = self.canvas
        total = len(words)
        mx_ds = 25
        if total > 1:
            x = 250 
            y = 250
            a = -170#float(input('a (-100): '))
            b = 2.5#float(input('b (2): '))
            ths = 85 #int(input('theta (50): '))
            thm = 5#float(input('theta mod (5): '))
            cv.delete('all')
            #Min max solver for scaling
            mx = int(counts[0])
            if total < mx_ds:
                mx_ds = total
            mn = int(counts[mx_ds-1])
            #Drawing function
            for j in range(mx_ds):
                radius = scale_range(int(counts[j]), mn, mx, 10, 40)
                """
                if radius > 30:
                    thm = 20
                elif radius > 25:
                    thm = 15
                elif radius > 20:
                    thm = 10
                elif radius > 15:
                    thm = 5
                elif radius > 10:
                    thm = 2
                """
                #thm = (radius-j*2) #* (j/(1.1*j+1))
                t = j
                th = j*thm + ths
                r = a + b*th
                nx = r*math.cos(t) + 250
                ny = r*math.sin(t) + 250
                #cv.create_line(x,y,nx,ny)
                if nx < self.canwidth and ny < self.canheight:
                    x = nx
                    y = ny
                else:
                    break
                cv.create_oval(x-radius, y-radius, x+radius, y+radius)
                cv.create_text((x,y), text=words[j])
        #x = input('Cont?')
        #if x != 'stop':
            #self.word_map(words, counts)

    def word_map_test2(self, words, counts):
        """Method for rendering word map onto canvas"""
        cv = self.canvas
        total = len(words)
        mx_ds = 25
        if total > 1:
            x = 250 
            y = 250
            a = -170#float(input('a (-100): '))
            b = 2#float(input('b (2): '))
            ths = 0#int(input('theta (50): '))
            thm = 1#float(input('theta mod (1): '))
            cv.delete('all')
            thm = range(50, 0, -5)
            #Min max solver for scaling
            mx = int(counts[0])
            if total < mx_ds:
                mx_ds = total
            mn = int(counts[mx_ds-1])
            #Drawing function
            for j in range(mx_ds):
                radius = scale_range(int(counts[j]), mn, mx, 10, 40)
                #thm = (radius-j*2) #* (j/(1.1*j+1))
                th = math.degrees(thm[j]) 
                r = radius*4
                nx = (r*math.cos(th))
                ny = (r*math.sin(th))
                #cv.create_line(x,y,nx,ny)
                if x + nx < self.canwidth and ny < self.canheight:
                    x += nx
                    y += ny
                else:
                    break
                cv.create_oval(x-radius, y-radius, x+radius, y+radius)
                cv.create_text((x,y), text=words[j])
        #x = input('Cont?')
        #if x != 'stop':
            #self.word_map(words, counts)
    
    def disp_msg(self, msg):
        """Simple method for displaying popup message"""
        popup = Tk()
        popup.wm_title("Message")
        popup.geometry('%dx%d+%d+%d' % (300, 100, 350, 350))
        pop_lab = Label(popup, text=msg)
        pop_lab.pack(side='top')
        ok_but = Button(popup, text="OK", command=popup.destroy)
        ok_but.pack()
    
    def disphelp(self):
        """Method for displaying help page"""
        popup = Tk()
        popup.wm_title("Help")
        popup.geometry('%dx%d+%d+%d' % (300, 560, 350, 150))
        pop_lab = Label(popup, text=help)
        pop_lab.pack(side='top')
        ok_but = Button(popup, text="OK", command=popup.destroy)
        ok_but.pack()

def scale_range(x, mn, mx, a, b):
    """Function for scaling range into another range"""
    output = (((b - a) * (x - mn) )/(mx - mn)) + a
    return output

def main():
    root = Tk()
    app = App(root)
    root.mainloop()  

help = (
"""
VI Assessment Tool
*Written by Connor Bechler in Summer 2020*

*This is a basic qualitative analysis application.
It segments text documents into questions, and 
allows the user to search their contents by words 
and phrases (in the search tab). 

*The user can also count how often words occur,
either by total occurence or by the number of 
times they've been used in different documents/
by different people/interviewees (in the count 
tab). This also produces a visualization of which
words occur the most often.

*Word documents can be directly imported by using 
the "Import" option in the file menu. This should 
perform all necessary cleaning operations and 
open the contents of a given directory.

*Alternatively, you can import plain text files
via the "Open" option in the file menu (select a 
directory which has only plain text files you want 
imported). However, the files in that directory must 
be cleaned and formatted properly. You can do this 
by adding the text "**0. Background\\n" and the name
of the interviewee and then using the "Clean" option
from the file menu to add section break characters.

*If you have any questions, please email them to
connorbechler@vianswers.com

""")

if __name__ == '__main__':
    main()  