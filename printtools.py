"""
Group of data printing tools developed by Connor Bechler
"""

def print_data(data):
    """Function for formatting and outputting different data types"""
    form_string = '{val:^5}'
    output = ""
    wdat = conv_dict(data)
    for x in range(len(wdat)):
        if iterable(wdat[x]):
            wdat[x] = conv_dict(wdat[x])
            for y in range(len(wdat[x])):
                if iterable(wdat[x][y]) and len(wdat[x][y]) > 1:
                    wdat[x][y] = conv_dict(wdat[x][y])
                    for z in range(len(wdat[x][y])):
                        if iterable(wdat[x][y][z]):
                            wdat[x][y][z] = conv_dict(wdat[x][y][z])
                            for j in range(len(wdat[x][y][z])):
                                output += form_string.format(val=str(wdat[x][y][z][j]) + " ")
                        else:
                            output += form_string.format(val=str(wdat[x][y][z]))
                else :
                    output += form_string.format(val=str(wdat[x][y]) + " ")
            output += "\n"
        else :
            output += form_string.format(val=str(wdat[x])) + '\n'
    
    return(output)

def print_data_better(data):

    form_string = '{val:^5}'
    output = ""
    for x in range(len(data)):
        wdat = conv_dict(data)
        if iterable(wdat[x]):
            try :    
                for y in range(len(wdat[x])):
                    if iterable(wdat[x][y]):
                        try :
                            for z in range(len(wdat[x][y])):
                                if iterable(wdat[x][y][z]):
                                    try:
                                        for j in range(len(wdat[x][y][z])):
                                            if iterable(wdat[x][y][z][j]):
                                                try:
                                                    for k in range(len(wdat[x][y][z][j])):
                                                        if iterable(wdat[x][y][z][j]):
                                                            try:
                                                                for l in range(len(wdat[x][y][z][j][k])):
                                                                    output += '6 ' + form_string.format(val=str(wdat[x][y][z][j][k][l]) + " ")
                                                            except :
                                                                output += '5b ' + form_string.format(val=str(wdat[x][y][z][j][k]) + " ")
                                                        else :
                                                            output += '5a ' + form_string.format(val=str(wdat[x][y][z][j][k]) + " ")
                                                except :
                                                    output += '4b ' + form_string.format(val=str(wdat[x][y][z][j]) + " ")   
                                            else:
                                                output += '4a ' + form_string.format(val=str(wdat[x][y][z][j]) + " ")
                                    except :
                                        output += '3b ' + form_string.format(val=str(wdat[x][y][z]) + " ")
                                else : 
                                    output += '\t' + '3a ' + form_string.format(val=str(wdat[x][y][z]) + " ")
                        except :
                            output += '2b ' + form_string.format(val=str(wdat[x][y]) + " ")
                    else :
                        output += '2a ' + form_string.format(val=str(wdat[x][y]) + " ") + '\n'
            except :
                output += '1b ' + form_string.format(val=str(wdat[x]) + " ")
            output += "\n"
        else:
            output += '1a ' + form_string.format(val=str(wdat[x])) + '\n'

    return(output)

def print_adv(inpt, l0o=' ', l0e=' ', l1o=' ', l1e=' ', l2o=' ', l2e=' ', l3o=' ', l3e=' ', l4o=' ', l4e=' ', 
l5o=' ', l5e=' ', l6o=' ', l6e=' ', l7o=' ', l7e=' ', l8o=' ', l8e=' ', l9o=' ', l9e=' ', mid = None, col=5):
    """Function for printing complex iterable data with user formatting"""
    
    inter = [' ' for x in range(9)]
    if isinstance(mid, str):
        intra = mid.split(' ')
        for x in range((len(intra)+1)//2): 
            inter[int(intra[x*2])] = str(intra[x*2+1])

    form_string = '{val:<' + str(col) + '}'  
    output = ""
    
    work = conv_dict(inpt)
    if iterable(work):
        for a in work:
            aa = conv_dict(a)
            if iterable(aa):
                for b in aa:
                    bb = conv_dict(b)
                    if iterable(bb):
                        for c in bb:
                            cc = conv_dict(c)
                            if iterable(cc):
                                for d in cc:
                                    dd = conv_dict(d)
                                    if iterable(dd):
                                        for e in dd:
                                            ee = conv_dict(e)
                                            if iterable(ee):
                                                for f in ee:
                                                    ff = conv_dict(f)
                                                    if iterable(ff):
                                                        for g in ff:
                                                            gg = conv_dict(g)
                                                            if iterable(gg):
                                                                for h in gg:
                                                                    hh = conv_dict(h)
                                                                    if iterable(hh):
                                                                        for i in hh:
                                                                            ii = conv_dict(i)
                                                                            output += l9o + form_string.format(val=str(ii)) + l9e
                                                                        output += inter[9]
                                                                    else:
                                                                        output += l8o + form_string.format(val=str(hh)) + l8e
                                                                output += inter[8]
                                                            else:
                                                                output += l7o + form_string.format(val=str(gg)) + l7e
                                                        output += inter[7]
                                                    else:
                                                        output += l6o + form_string.format(val=str(ff)) + l6e
                                                output += inter[6]
                                            else :
                                                output += l5o + form_string.format(val=str(ee)) + l5e 
                                        output += inter[5]
                                    else :
                                        output += l4o + form_string.format(val=str(dd)) + l4e
                                output += inter[4]
                            else :
                                output += l3o + form_string.format(val=str(cc)) + l3e
                        output += inter[3]
                    else :
                        output += l2o + form_string.format(val=str(bb)) + l2e
                output += inter[2]
            else :
                output += l1o + form_string.format(val=str(aa)) + l1e
        output += inter[1]
    else :
        output += l0o + form_string.format(val=str(work)) + l0e
        output += inter[0]

    return(output)                                            

def format_count_table(counts, maxcols=6, colwidth=20):
    """Takes a count dictionary, sorts it, and builds it into a CLI displayable table"""
    counts = conv_dict(counts)
    if len(counts) >= maxcols:
        cols = maxcols
    else :
        cols = len(counts)
    rows = (len(counts) // cols) + 1
    row = '{val:<' + str(colwidth) + '}'
    output = ''
    table = [[' ' for i in range(cols)] for j in range(rows)]
    x = 0
    y = 0
    for k in range(len(counts)):
        table[y][x] = counts[k][0] + ': ' + str(counts[k][1])
        if y < rows-1:
            y += 1
        else :
            y = 0
            x += 1
    for v in table :
        for l in v:
            output += row.format(val=l)
        output += '\n'        
    return output

def format_conc_lines(conclines):
    """Takes concordance line input and outputs as a CLI friendly string"""
    form_string = '{sec:<6}{line:<6}{lcon:>50}{foc:^15}{rcon:<50}'
    output = ''
    for x in conclines:
        output += form_string.format(sec=str(x[0]),line=str(x[1]),lcon=x[2],foc=x[3],rcon=x[4]) + '\n'
    return output

def sort_dict(inpt):
    """Function for sorting count dictionaries from highest to lowest into tuples"""
    if isinstance(inpt[list(inpt)[0]], int):
        output = sorted(inpt.items(), key=lambda x: x[1], reverse=True)
    if isinstance(inpt[list(inpt)[0]], list) and isinstance(inpt[list(inpt)[0]][0], int):
        newdct = {}
        for key in list(inpt):
            newdct[key] = inpt[key][0]
        output = sorted(newdct.items(), key=lambda x: x[1], reverse=True)
    return output

def conv_dict(dct):
    """Function for checking if dict, and if so converting to sorted tuple"""
    if isinstance(dct, dict):
            if isinstance(dct[list(dct)[0]], int):
                dct = sort_dict(dct)
            else:
                dct = list(dct.items())
    return dct

def iterable(var):
    """Modified function from
    https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable"""
    
    try:
        iter(var)
        if isinstance(var, str):
            raise Exception
    except Exception:
        return False
    else :
        return True