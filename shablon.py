# -*- coding: utf-8 -*-

from copy import copy
import time
import codecs


class Word():
    def __init__(self, sentence):  # значения по умолчанию для головы, если головы этапа и синт атома совпадают
        self.sent = sentence
        self.index = u''  # порядковый номер от начала предложения
        self.token = u''
        self.sa_lemma = u''
        self.sa_gramm = u''
        self.sa_head = u'root'
        self.sa_link = u'root'
        self.et_head = u''
        self.et_head_index = 0  # порядковый номер от начала предложения того слова, которое является головой в этапе
        self.et_link = u'~'
        self.et_gramm = u''
        self.ud_head = u'root'
        self.ud_link = u'root'
        self.ud_lemma = u''
        self.ud_gramm = u''
        self.direction = False  # нужно ли менять направление стрелки
        self.head_change = False  # нужно ли менять голову
        self.sa_children = []
        self.et_children = []

    def add_child(self, tok, ind, sa_lem, sa_gr, sa_lin, et_gr, et_lin, sentence, et_head_ind):
        child = Word(sentence)
        child.index = ind
        child.token = tok
        child.sa_lemma = sa_lem
        child.sa_gramm = sa_gr
        child.sa_head = self
        child.sa_link = sa_lin
        child.et_head_index = et_head_ind
        child.et_link = et_lin
        child.et_gramm = et_gr
        self.sa_children.append(child)
        return child

    def hard(self, info, where):  # это просто про совпадение
            if info[2] == where:
                self.ud_link = info[3]
            else:
                self.ud_link = info[0]

    def hard_in(self, info, where):  # про содержание, для грамматики (например, "acc" содержится в "fem,trd,sg,acc,nn")
            if info[2] in where:
                self.ud_link = info[3]
            else:
                self.ud_link = info[0]

    def ud_convert_shablon(self, info):
        if info[1] == u'-':
            self.ud_link = info[0]
            # print u'simple translation', self.sa_link, u'to', self.ud_link
        else:
            if info[1] == u'etap3':
                self.hard(info, self.et_link)
            elif info[1] == u'gramm':
                self.hard_in(info, self.sa_gramm)
            elif info[1] == u'head_gramm':
                self.hard_in(info, self.sa_head.sa_gramm)
            elif info[1] == u'head_token':
                self.hard(info, self.sa_head.token)
            elif info[1] == u'token':
                self.hard(info, self.token)
            elif info[1] == u'head_link':
                self.hard(info, self.sa_head.link)
            elif info[1] == u'soft':
                self.ud_convert()
            else:
                print u'unexpected "where" in shablon, typo? ', info[1]
        self.ud_head = self.sa_head
        if info[4] == u'T':
            self.head_change = True

    def ud_convert(self):
        # это, конечно, не надо всё в кучу в одном месте писать, но пока я оставила так
        self.ud_gramm = self.sa_gramm  # наверное в перспективе тут тоже будет что-то меняться? мы не говорили об этом
        self.ud_lemma = self.sa_lemma
        if self.sa_link == u'root':
            self.ud_link = u'root'
            self.ud_head = u'root'
        if self.sa_link == u'subj:nom':
            self.ud_link = u'nsubj'
            self.ud_head = self.sa_head
        if self.sa_link == u'dat':
            if self.et_link == u'1-компл':
                self.ud_link = u'dobj'
            elif self.et_link == u'2-компл':
                self.ud_link = u'iobj'
            else:
                pass
                # на самом деле тут наверняка будут предложения с ошибками, а может и просто неучтенные случаи
            self.ud_head = self.sa_head
        if self.sa_link == u'obj:acc':
            self.ud_link = u'dobj'
            self.ud_head = self.sa_head
        if self.sa_link == u'obj:acc:coord':
            self.ud_link = u'conj'
            self.ud_head = self.sa_head
        if self.sa_link == u'conj':
            self.ud_link = u'cc'
            self.head_change = True
            self.ud_head = self.sa_head
            # self.ud_head = self.sa_head.sa_head
            # ОН сказала пока не делать правильной ud головы, а помечать места смены структуры
            # (что и делает строка self.head_change = True)
            # но я написала на всякий случай, что в итоге должно происходить - self.ud_head = self.sa_head.sa_head


class Sent():
    def __init__(self):
        self.index = u''
        self.text = u''
        self.root = Word(self)
        self.words = {}

    def print_sa_tree(self):
        print u'synt atom tree:'
        for child in sorted(self.words):
            if self.words[child].sa_link != u'root':
                try:
                    print child, self.words[child].token, u'←', self.words[child].sa_head.token, u' : ', self.words[child].sa_link
                except:
                    print u'no head', u' : ', self.words[child].sa_link
            else:
                print child, self.words[child].token, u' : root'

    def print_et_tree(self):
        print u'etap-3 tree:'
        for child in sorted(self.words):
            if self.words[child].et_link != u'root':
                print self.words[child].token, u'←', self.words[child].et_head.token, u' : ', self.words[child].et_link
            else:
                print self.words[child].token, u' : root'

    def create_ud_tree(self):
        filo = copy(self.root.sa_children)
        for child in filo:
            if child.sa_link in link_dict:
                child.ud_convert_shablon(link_dict[child.sa_link])
            else:
                print u'unknown link ', child.sa_link
                child.ud_head = child.sa_head
                child.ud_link = u'dep'
            filo += child.sa_children

    def print_ud_tree(self):
        print u'universal dependencies tree:'
        for child in sorted(self.words):
            if self.words[child].ud_link != u'root':
                print self.words[child].token, u'←', self.words[child].ud_head.token, u' : ', self.words[child].ud_link
            else:
                print self.words[child].token, u' : root'

    def create_structure(self):
        # words_arr = {}
        # print self.words
        for index in self.words:
            if self.words[index].sa_head_index == 0:
                if self.words[index].sa_gramm != u'pnt':
                    self.root = self.words[index]
                else:  # знаки препинания, которые ни на чем не висят, перевешиваем на корень
                    self.root.sa_children.append(self.words[index])
                    self.words[index].sa_head = self.root
                continue
            # print child.token, child.sa_head.index
            # words_arr[child.index] = child
            self.words[self.words[index].sa_head_index].sa_children.append(self.words[index])
            self.words[index].sa_head = self.words[self.words[index].sa_head_index]
            try:
                self.words[self.words[index].et_head_index].et_children.append(self.words[index])
                self.words[index].et_head = self.words[self.words[index].et_head_index]
            except:
                # Это значит, что в Этапе корень не совпадает с корнем синт атома.
                # В этапе все знаки препинания по сути корни, как это ни комично, поэтому они тоже оказываются здесь
                pass
            # print u'etap structure', self.words[index].token, self.words[self.words[index].et_head_index].token
        # self.words = words_arr


def create_link_dict():
    cs = codecs.open(u'cond_shablon.txt', u'r', u'utf-8')
    link_dict = {}
    for line in cs:
        line = line.rstrip()
        line = line.split(u'	')
        # print line
        link_dict[line[0]] = line[1:]
        # print line[0], link_dict[line[0]], u'link dict creation'
    return link_dict


link_dict = create_link_dict()
tc = codecs.open(u'corpus-shablon.txt', u'r', u'utf-8')
ud = codecs.open(u'ud.txt', u'w', u'utf-8')
ud.write(u'sent	sid	wid	token	lemma	gram	head	link\r\n')
previous_sent = Sent()
previous_sent.index = -1
for line in tc:
    # print line, line[0], u'this is line', line[0], line[1]
    if line[0] == u's':
        # print line, u'first_line'
        first = True
        continue
    line = line.rstrip()
    line_content = line.split(u'	')
    if line_content[1] != previous_sent.index:
        first = True
    if first:
        if previous_sent.index != -1:
            previous_sent.create_structure()
            previous_sent.print_sa_tree()
            # previous_sent.print_et_tree()
            previous_sent.create_ud_tree()
            print
            previous_sent.print_ud_tree()
            for child in sorted(previous_sent.words):
                    word = previous_sent.words[child]
                    if word.ud_link == u'root':
                        arr = [previous_sent.text, previous_sent.index, str(word.index), word.token, word.sa_lemma, word.sa_gramm, u'0',u'root']
                    else:
                        arr = [previous_sent.text, previous_sent.index, str(word.index), word.token, word.sa_lemma, word.sa_gramm, str(word.ud_head.index), word.ud_link]
                    # print arr
                    towrite = u'	'.join(arr)
                    ud.write(towrite + u'\r\n')
            print u'_________________________________________________'
        new_sent = Sent()
        new_sent.index = line_content[1]
        new_sent.text = line_content[0]
    new_word = Word(new_sent)
    new_word.sent_index = line_content[1]
    new_word.sent_text = line_content[0]
    new_word.index = int(line_content[2])
    new_word.token = line_content[3]
    new_word.sa_lemma = line_content[4]
    new_word.sa_gramm = line_content[5]
    new_word.sa_head_index = int(line_content[6])
    new_word.sa_link = line_content[7]
    try:
        new_word.et_lemma = line_content[9]
    except:
        print line, u'no index 9 here'
    new_word.et_gramm = line_content[10]
    new_word.et_head_index = int(line_content[11])
    try:
        new_word.et_link = line_content[12]
    except:
        new_word.et_link = u''
    new_sent.words[int(new_word.index)] = new_word
    if new_word.sa_head == 0:
        new_sent.root = new_word
    previous_sent = new_sent
    first = False