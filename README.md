# ud_sa_scripts
скрипт для конвертации syn atom в universal dependencies
вот здесь лежат скрипты и шаблоны.

Шаблоны пишутся в файле cond_shablon. Если для перевода не нужно никаких правил, то нужно заполнить только поля sa_link и default_ud_link.
Если нужны простые правила, в поле where нужно написать что-то из списка

    etap3
    token
    gramm
    head_token
    head_gramm
    head_link

Я не знаю, нужно ли нам что-то еще, но всегда можно добавить.
В поле what нужно написать значение переменной, в поле then_ud_link - то, какая связь ставится, если where == what или what содержится в where (для грамматики).
Например, такая штука
sa_link    default_ud_link    where          what    then_ud_link    head_change
s_link      u_link_1             head_token  быть   u_link_2           -
обозначает, что связь "s_link" переводится в "u_link_2", если слово зависит от "быть" и в "u_link_2" в противном случае.

Если необходимо более сложное условие, то в where нужно написать soft, а само условие прописать в шаблоне внутри функции ud_convert.
Все незаполненные поля нужно заполнить минусиками (это довольно тупо, но иначе для того чтобы просплитить исходный файл нужно будет импортировать регулярные выражения, а мне не хочется этого делать ради одного использования).

В поле head_change нужно написать T, если в этом месте в будущем необходимо изменение структуры.

Если связь из synt atom не нашлась в файле шаблонами, в связь UD пишется dep, голова копируется.

NB:
1) все замены, которые сейчас внутри функции ud_convert НЕ НУЖНЫ, они там написаны просто как пример, как можно писать правила, а эти связи обработаны через шаблон
2) в шаблоне для dat прописано не то что там на самом деле должно быть, это просто пример
3) в where можно написать что угодно еще, если нужно (например, etap_head_link), но тогда нужно добавить пару строк про это в функции ud_convert_shablon по аналогии с другими.

Все потом пишется в файл ud.txt.
Исходные файлы должны быть в utf-8 БЕЗ BOM
Файл corpus-shablon переводится нормально, там только известные связи, и вообще всё хорошо.
В основном файле корпуса много ошибок выравнивания разметки etap-3 и synt atom, поэтому его перевести пока не удается, но в принципе он нормально открывается, и парсится, и пишется до тех пор пока не упадет на предложении с ошибкой.
