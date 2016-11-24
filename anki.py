#! /usr/bin/env python
import itertools
import os
import subprocess

src_dir = 'src/reasoned'

filenames = os.listdir(src_dir)

def parser(segments):
    xs = []
    for is_comment, group in itertools.groupby(segments, lambda s: s.startswith(';;')):
        if is_comment:
            gs = map(lambda s: s[3:].strip(), group) # take ';;<' and ';;>' off, remove extra spaces
            s = ' '.join(gs) # combine multiline comments into one string
            xs.append({'text': s})
        else:
            xs.append({'code': ''.join(group)})
    return xs

def process_segment(segment):
    try:
        i = (i for i,s in enumerate(segment) if s.startswith(';;<')).next()
        return {'question': parser(segment[0:i]), 'answer': parser(segment[i:])}
    except StopIteration:
        return {'expression': parser(segment)}

for filename in filenames[0:1]:
    with open(os.path.join(src_dir, filename), 'r') as f:
        segments = []
        accumulator = []
        # This for loop splits code into segments, dividing using 1 or more blank lines
        for is_empty, group in itertools.groupby(f.readlines(), lambda s: len(s.strip()) == 0):
            if not is_empty:
                segments.append(list(group))

        ns_declaration = segments.pop(0) # pop the ns declaration
        accumulator.append(''.join(ns_declaration)) # add ns declaration to begining of accumulator
        segments = map(process_segment, segments)

        for segment in segments:
            for k,vs in segment.items():
                for section in vs:
                    if 'code' in section:
                        accumulator.append(section['code'])
                        s = ' '.join(accumulator)
                        CMD = ['boot', 'load-code', '-c', '%s' % s]
                        try:
                            section['result'] = subprocess.check_output(CMD)
                        except subprocess.CalledProcessError:
                            print "===== CODE ======"
                            print evaled
                            print "===== CMD ======="
                            print ' '.join(CMD)
                            raise

        cards = ['\t']
        for segment in segments:
            if 'expression' in segment:
                d = segment['expression'][0]
                cards.append('%s\t%s' % (d['code'], d['result']))
            else:
                question = []
                for d in segment['question']:
                    if 'text' in d:
                        question.append(d['text'])
                    else:
                        question.append(d['code'].strip())
                        question.append(' => %s' % d['result'])
                question = '\n'.join(question)
                cards.append('%s\t%s' % (question, segment['answer'][0]['text']))

        print '\n'.join(cards)
