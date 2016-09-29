
# -*- coding: utf-8 -*-

import codecs
from copy import copy
import random


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
        self.ud_pos = u''
        self.direction = False  # нужно ли менять направление стрелки
        self.head_change = False  # нужно ли менять голову
        self.sa_children = []
        self.et_children = []
        self.et_lemma = u''
        self.et_token = u''

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

    def get_pos(self):
        if self.et_gramm == u'' or self.et_gramm == u'~':
            self.ud_pos = u'PUNCT'
        elif u'S' in self.et_gramm:
            self.noun()
        elif u'ADV' in self.et_gramm:
            self.ud_pos = u'ADV'
        elif u'V' in self.et_gramm:
            if u'adj' in self.sa_gramm:
                if u'pst' not in self.sa_gramm:
                    self.ud_pos = u'ADJ'
                else:
                    self.ud_pos = u'V'
                    self.sa_gramm += u',ptc'
            elif u'nn' in self.sa_gramm:
                self.ud_pos = u'NOUN'
            else:
                self.ud_pos = u'VERB'
        elif u'AUX' in self.et_gramm:
            self.ud_pos = u'AUX'
        elif self.et_gramm[0] == u'A':
            if u'СРАВ' in self.et_gramm:
                self.ud_pos = u'ADV'
            else:
                self.ud_pos = u'ADJ'
        elif u'PART' in self.et_gramm:
            self.ud_pos = u'PART'
        elif u'PR' in self.et_gramm:
            self.ud_pos = u'ADP'
        elif u'NID' in self.et_gramm:
            self.ud_pos = u'PROPN'
        elif u'NUM' in self.et_gramm:
            self.ud_pos = u'NUM'
        elif u'INTJ' in self.et_gramm:
            self.ud_pos = u'INTJ'
        elif u'CONJ' in self.et_gramm:
            self.conj()
        elif u'COM' in self.et_gramm:
            self.ud_pos = u'X'
        else:
            print u'unknown pos', self.token, self.et_gramm

    def get_person(self):
                    if u'fst' in self.sa_gramm:
                        person = 1
                    elif u'sec' in self.sa_gramm:
                        person = 2
                    elif u'trd' in self.sa_gramm:
                        person = 3
                    else:
                        print u'what the person', self.token, self.sa_gramm
                    return str(person)

    def get_gramm(self):
        imena = u'NOUN ADJ PROPN PRON'.split(u' ')
        nouns = u'NOUN PROPN'
        if self.ud_pos in imena:
            number = self.get_number()
            case = self.get_case()
            if self.ud_pos in nouns:
                gender = self.get_gender()
                anim = self.get_animacy()
                return u','.join([number, gender, case, anim])
            if self.ud_pos == u'ADJ':
                degree = self.get_degree()
                if degree == u'Cmp':
                    return u','.join([number, case, degree])
                if number == u'Plur':
                    if u'sht' in self.sa_gramm:
                        return u','.join([number, u'strong'])
                    return u','.join([number, case, degree])
                gender = self.get_gender()
                if u'sht' in self.sa_gramm:
                    return u','.join([number, gender, u'strong'])
                return u','.join([number, gender, case, degree])
            gender = self.get_gender()
            return u','.join([number, gender, case])
        elif self.ud_pos == u'ADV':
            degree = self.get_degree()
            return degree
        elif self.ud_pos == u'VERB':
            if u'fin' in self.sa_gramm or u'imp' in self.sa_gramm:
                number = self.get_number()
                form = u'Fin'
                if u'imp' in self.sa_gramm:
                    mood = u'Imp'
                    return u','.join([number, form, mood])
                else:
                    mood = u'Ind'
                if u'prs' in self.sa_gramm:
                    tense = u'Pres'
                    person = self.get_person()
                    return u','.join([number, form, mood, tense, person])
                elif u'pst' in self.sa_gramm:
                    tense = u'Past'
                    if number == u'Sing':
                        gender = self.get_gender()
                        return u','.join([number, form, mood, tense, gender])
                    return u','.join([number, form, mood, tense])
                else:
                    print u'was für ein', self.sa_gramm, self.token
            elif u'inf' in self.sa_gramm:
                form = u'Inf'
                return form
            elif u'ptp' in self.sa_gramm:
                number = self.get_number()
                form = u'Part'
                voice = self.get_voice()
                case = self.get_case()
                ptc_tense = self.get_ptc_tense()
                return u','.join([number, form, voice, case, ptc_tense])
            elif u'dee' in self.sa_gramm:
                form = u'Trans'
                return form
            elif u'pdv' in self.sa_gramm:
                return u'pdv'
            else:
                print u'was für eine Form', self.sa_gramm, self.token
                return u'dif'  # нужно разобраться
        else:
            return u''

    def get_ptc_tense(self):
        if u'НЕПРОШ' in self.et_gramm:
            tence = u'Past'
        elif u'ПРОШ' in self.et_gramm:
            tence = u'Pres'
        else:
            print u'Что за время', self.token, self.sa_gramm, self.et_gramm
        return tence

    def get_voice(self):
            if u'psv' in self.sa_gramm:
                voice = u'Pass'
            else:
                voice = u'Act'
            return voice

    def get_animacy(self):
        if u'anm' in self.sa_gramm:
            anim = u'Anim'
        else:
            anim = u'Inan'
        return anim

    def get_degree(self):
        if u'cmp' in self.sa_gramm:
            return u'Cmp'
        else:
            return u'Pos'

    def get_case(self):
        if u'nom' in self.sa_gramm:
            case = u'Nom'
        elif u'gen' in self.sa_gramm:
            case = u'Gen'
        elif u'dat' in self.sa_gramm:
            case = u'Dat'
        elif u'acc' in self.sa_gramm:
            case = u'Acc'
        elif u'ins' in self.sa_gramm:
            case = u'Ins'
        elif u'loc' in self.sa_gramm:
            case = u'Loc'
        elif u'sht' in self.sa_gramm:
            case = u'strong'
        else:
            case = self.get_et_case()
        return case

    def get_et_case(self):
        if u'ИМ' in self.et_gramm:
            case = u'Nom'
        elif u'РОД' in self.et_gramm:
            case = u'Gen'
        elif u'ДАТ' in self.et_gramm:
            case = u'Dat'
        elif u'ВИН' in self.et_gramm:
            case = u'Acc'
        elif u'ТВОР' in self.et_gramm:
            case = u'Ins'
        elif u'ПР' in self.et_gramm:
            case = u'Loc'
        elif u'КР' in self.et_gramm:
            case = u'strong'
        elif u'NID' in self.et_gramm:
            return u''
        else:
            print u'was für ein Kasus', self.sa_gramm, self.et_gramm, self.token
            return u''
        return case

    def get_number(self):
        if u'sg' in self.sa_gramm:
            return u'Sing'
        elif u'pl' in self.sa_gramm:
            return u'Plur'
        else:
            number = self.get_et_number()
            return number

    def get_et_number(self):
            if u'ЕД' in self.et_gramm:
                return u'Sing'
            elif u'МН' in self.et_gramm:
                return u'Plur'
            elif u'NID' in self.et_gramm:
                return u''
            print u'was für ein number', self.et_gramm, self.sa_gramm, self.token
            return u''

    def get_gender(self):
        if u'neu' in self.sa_gramm:
            gender = u'Neut'
        elif u'msc' in self.sa_gramm:
            gender = u'Masc'
        elif u'fem' in self.sa_gramm:
            gender = u'Fem'
        else:
            gender = self.get_et_gender()
        return gender

    def get_et_gender(self):
            if u'СРЕД' in self.et_gramm:
                gender = u'Neut'
            elif u'МУЖ' in self.et_gramm:
                gender = u'Masc'
            elif u'ЖЕН' in self.et_gramm:
                gender = u'Fem'
            elif u'NID' in self.et_gramm:
                return u''
            else:
                print u'was für ein gender?', self.sa_gramm, self.et_gramm, self.token
                return u''
            return gender

    def conj(self):
        self.ud_pos = u'CONJ'

    def noun(self):
        if u'prn' in self.sa_gramm:
            self.ud_pos = u'PRON'
        elif u'-ЗНАК' in self.et_lemma:
            self.ud_pos = u'SYM'
        else:
            self.ud_pos = u'NOUN'

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
        try:
            if info[4] == u'T':
                self.head_change = True
        except IndexError:
            if info[0] not in cp_arr:
                cp.write(u'too short instruction: ' + self.sa_link + u'\r\n')
                cp_arr.append(info[0])

    def ud_convert(self):
        # это, конечно, не надо всё в кучу в одном месте писать, но пока я оставила так
        self.ud_gramm = self.sa_gramm  # наверное в перспективе тут тоже будет что-то меняться? мы не говорили об этом
        self.ud_lemma = self.sa_lemma
        # if self.sa_link == u'root':
        #     self.ud_link = u'root'
        #     self.ud_head = u'root'
        # if self.sa_link == u'subj:nom':
        #     self.ud_link = u'nsubj'
        #     self.ud_head = self.sa_head
        # if self.sa_link == u'dat':
        #     if self.et_link == u'1-компл':
        #         self.ud_link = u'dobj'
        #     elif self.et_link == u'2-компл':
        #         self.ud_link = u'iobj'
        #     else:
        #         pass
        #         # на самом деле тут наверняка будут предложения с ошибками, а может и просто неучтенные случаи
        #     self.ud_head = self.sa_head
        # if self.sa_link == u'obj:acc':
        #     self.ud_link = u'dobj'
        #     self.ud_head = self.sa_head
        # if self.sa_link == u'obj:acc:coord':
        #     self.ud_link = u'conj'
        #     self.ud_head = self.sa_head
        # if self.sa_link == u'conj':
        #     self.ud_link = u'cc'
        #     self.head_change = True
        #     self.ud_head = self.sa_head
        #     # self.ud_head = self.sa_head.sa_head
        #     # ОН сказала пока не делать правильной ud головы, а помечать места смены структуры
        #     # (что и делает строка self.head_change = True)
        #     # но я написала на всякий случай, что в итоге должно происходить - self.ud_head = self.sa_head.sa_head
        #сложные правила Маша
        if self.sa_link == u'np':
            if self.sa_lemma.startswith(u'QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪЭДЛОРПАВЫФЯЧСМИТЬБЮ'):
                self.ud_link = u'name'
            else:
                self.ud_link = u'vocative'
        if self.sa_link == u'card':
            if self.et_link == u'колич':
                self.ud_link = u'nummod:gov'
            if self.et_link == u'опред':
                self.ud_link = u'det:nummod'
            if self.et_link == u'1-компл':
                self.ud_link = u'det:numgov'
        if self.sa_link == u'inf':
            if self.et_link == u'присвяз':
                self.ud_link = u'cop'
            if self.ud_pos == u'NOUN':
                self.ud_link = u'acl'
            else:
                self.ud_link = u'ccomp'
        if self.sa_link == u'appo':
            if self.sa_head.lemma.startswith(u'QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪЭДЛОРПАВЫФЯЧСМИТЬБЮ'):
                self.ud_link = u'nmod'
            if self.sa_head.lemma.startswith(u'QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪЭДЛОРПАВЫФЯЧСМИТЬБЮ') \
                    and self.sa_lemma.startswith(u'QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪЭДЛОРПАВЫФЯЧСМИТЬБЮ'):
                self.ud_link = u'name'
            else:
                self.ud_link = u'appos'
        if self.sa_link == u'misc':
            if self.ud_pos == u'PUNCT':
                self.ud_link = u'punct'
            elif self.sa_lemma.startswith(u'QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪЭДЛОРПАВЫФЯЧСМИТЬБЮ'):
                self.ud_link = u'name'
            else:
                self.ud_link = u'dep'
        if self.sa_link == u'conj':
            if self.sa_lemma == u'и' or self.sa_lemma == u'да' or self.sa_lemma == u'или' or self.sa_lemma == u'либо' \
                    or self.sa_lemma == u'тоже' or self.sa_lemma == u'также' or self.sa_lemma == u'притом' or self.sa_lemma == u'причём' \
                    or self.sa_lemma == u'а' or self.sa_lemma == u'но' or self.sa_lemma == u'зато' or self.sa_lemma == u'однако' or self.sa_lemma == u'же':
                self.ud_link = u'cc'
            else:
                self.ud_link = u'advmod'
        
        

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
                except AttributeError:
                    # print self.words[child].sa_head, u'has no token'
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
        filo = copy(self.root.sa_children)  # запускается для детей корня, потом для детей детей
        for child in filo:
            if child.sa_link in link_dict:
                if child.sa_link == u'root':
                    print u'this is the root:', child.token, u'when we already have a root', self.root.token
                    bs.write(self.index + u'\t' + self.text + u'	more than one root')
                child.ud_convert_shablon(link_dict[child.sa_link])
            else:
                if child.sa_link not in written_links:
                    written_links[child.sa_link] = 1
                else:
                    written_links[child.sa_link] += 1
                # print u'unknown link ', child.sa_link
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
        foundroot = False
        for index in self.words:
            if self.words[index].sa_link == u'root':
                foundroot = True
                self.words[index].sa_head_index = 0  # мб лучше такие предложения убивать?
                # Это те, где у головы есть голова...
                self.root = self.words[index]
                break
        if not foundroot:
            # предложение без корня
            bs.write(self.index + u'\t' + self.text + u'\tno root' + u'\r\n')
            return False
        for index in self.words:
            if self.words[index].sa_head_index == 0:
                if self.words[index].sa_link == u'root':  # если это действительно корень
                    self.root = self.words[index]
                else:  # если у этого просто так головы нет, берем его голову из этапа
                    et_ind = self.words[index].et_head_index
                    if et_ind == 0 or self.words[index].sa_gramm == u'pnt':  # но если и у этапа нет головы или
                        # это пунктуация, перевешиваем это слово на корень
                        self.root.sa_children.append(self.words[index])
                        self.words[index].sa_head = self.root
                    else:
                        self.words[et_ind].sa_children.append(self.words[index])
                        self.words[index].sa_head = self.words[et_ind]
                continue
            # print child.token, child.sa_head.index
            # words_arr[child.index] = child
            try:
                self.words[self.words[index].sa_head_index].sa_children.append(self.words[index])
                self.words[index].sa_head = self.words[self.words[index].sa_head_index]
            except KeyError:
                print u'key error, index', index, u', when max index is', len(self.words) - 1, u'; sa_head_index', \
                    self.words[index].sa_head_index, u'in the sent', self.index
                bs.write(self.index + u'\t' + self.text + u'\tbad indexing' + u'\r\n')
                return False
            try:
                self.words[self.words[index].et_head_index].et_children.append(self.words[index])
                self.words[index].et_head = self.words[self.words[index].et_head_index]
            except:
                # Это значит, что в Этапе корень не совпадает с корнем синт атома.
                # В этапе все знаки препинания по сути корни, как это ни комично, поэтому они тоже оказываются здесь
                pass
            # print u'etap structure', self.words[index].token, self.words[self.words[index].et_head_index].token
        # self.words = words_arr
        return True


def create_link_dict():
    cs = codecs.open(u'cond_shablon.txt', u'r', u'utf-8')
    link_dict = {}
    for line in cs:
        line = line.rstrip()
        if u'>' in line or u'<' in line or line == u'':
            continue
        line = line.split(u'	')
        # print line
        link_dict[line[0]] = line[1:]
        # print line[0], link_dict[line[0]], u'link dict creation'
    return link_dict


def write_ul():
    for link in written_links:
        ul.write(u'unknown link ' + link + u'\t' + str(written_links[link]) + u'\r\n')


def get_random(gsc, total):
    if gsc >= 200:
        return False, gsc, total
    a = random.randint(0, total - gsc)
    if a <= 200:
        gsc += 1
        return True, gsc, total
    return False, gsc, total


link_dict = create_link_dict()
ul = codecs.open(u'unknown_links.txt', u'w', u'utf-8')
ov = codecs.open(u'ошибка выравнивания.txt', u'w', u'utf-8')
cp = codecs.open(u'проблемы в шаблоне.txt', u'w', u'utf-8')
cp_arr = []
bs = codecs.open(u'bad_sentence.txt', u'w', u'utf-8')
tc = codecs.open(u'corpus-shablon.txt', u'r', u'utf-8')
tc = codecs.open(u'C:\\Tanya\\universal_dependencies\\corpus-d_2304.txt', u'r', u'utf-8')
ud = codecs.open(u'C:\\Tanya\\universal_dependencies\\corpus_ud_2909.txt', u'w', u'utf-8')
gs = codecs.open(u'C:\\Tanya\\universal_dependencies\\gold_standard.txt', u'w', u'utf-8')
written_links = {}
ud.write(u'sent	sid	wid	token	lemma	gram	head	link\r\n')
gs.write(u'sent	sid	wid	token	lemma	gram	head	link\r\n')
previous_sent = Sent()
previous_sent.index = -1
gsc = 0
total = 15443
for line in tc:
    line = line.rstrip()
    if u'>' in line or u'<' in line or line == u'' or line[0] == u's':
        first = True
        # print line, u'the beginning'
        continue
    line_content = line.split(u'\t')
    # print line, u'begins with', line_content[0]
    # print u'the second item', line_content[1], previous_sent.index
    if line_content[1] != previous_sent.index:
        # print u'that is the first', line_content[3]
        first = True
    if first:
        if previous_sent.index != -1 and not ovm and not bad_sentence:
            total -= 1
            created = previous_sent.create_structure()
            if created:
                # previous_sent.print_sa_tree()
                # previous_sent.print_et_tree()
                previous_sent.create_ud_tree()
                # print
                # previous_sent.print_ud_tree()
                iftake, gsc, total = get_random(gsc, total)
                for child in sorted(previous_sent.words):
                        word = previous_sent.words[child]
                        if word.ud_link == u'root':
                            arr = [previous_sent.text, previous_sent.index, str(word.index), word.token, word.sa_lemma,
                                   word.ud_pos, word.ud_gramm, u'0',u'root']
                        else:
                            arr = [previous_sent.text, previous_sent.index, str(word.index), word.token, word.sa_lemma,
                                   word.ud_pos, word.ud_gramm, str(word.ud_head.index), word.ud_link]
                        # print arr
                        towrite = u'	'.join(arr)
                        ud.write(towrite + u'\r\n')
                        if iftake:
                            gs.write(towrite + u'\r\n')
                # print u'_________________________________________________'
        ovm = False
        bad_sentence = False
        new_sent = Sent()
        new_sent.index = line_content[1]
        previous_sent.index = new_sent.index
        new_sent.text = line_content[0]
        if line_content[2] != u'1':
            # это ломанное предложение
            bs.write(new_sent.index + u'\t' + new_sent.text + u'\tfalse start' + u'\r\n')
            # print u'the reason fo false start is that the fist line is', line
            bad_sentence = True
            previous_sent = new_sent
        first = False
    if ovm or bad_sentence:
        continue
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
        new_word.et_token = line_content[8]
    except IndexError:
        ov.write(new_sent.index + u'\t' + new_sent.text + u'\r\n')
        ovm = True
        print u'ошибка выравнивания', new_sent.index
        continue
    if new_word.token != new_word.et_token:
        ov.write(new_sent.index + u'\t' + new_sent.text + u'\r\n')
        ovm = True
        # print u'токены не совпадают', new_word.token, new_word.et_token
        continue
    try:
        new_word.et_gramm = line_content[10]
    except IndexError:
        ov.write(new_sent.index + u'\t' + new_sent.text + u'\r\n')
        ovm = True
        continue
    new_word.et_head_index = int(line_content[11])
    try:
        new_word.et_link = line_content[12]
    except IndexError:
        new_word.et_link = u''
    new_word.get_pos()
    new_word.ud_gramm = new_word.get_gramm().replace(u',,,', u',').replace(u',,', u',')
    new_sent.words[int(new_word.index)] = new_word
    # if new_word.sa_head == 0:
    #     new_sent.root = new_word
    previous_sent = new_sent
    first = False

write_ul()
print u'gs len: ', gsc

