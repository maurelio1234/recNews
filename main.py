# based on https://www.bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

import feedparser
import linguistictagger as lt
import pickle
import math
import sys
import urllib
import string
import shutil
from datetime import datetime

def print_link(title, link):
	try:
		import console
		console.write_link(title, link)
	except ImportError:
		print 'Title: {0}, Link: {1}'.format(title, link)
		
def load_dataset():
	try:
		with open('dataset', 'rb') as g:
			dataset = pickle.load(g)
			return dataset
	except BaseException as be:
		print str(be)
		return None 
			
def save_dataset(dataset):
	backup_dataset()
	with open('dataset', 'wb') as g:
		pickle.dump(dataset,g)

def backup_dataset():
	shutil.copyfile('dataset', 'dataset.old.{:%Y%m%d}'.format(datetime.now()))
	
def build_training_set():
	print
	print 'Loading feed...'
	f = feedparser.parse('http://www.lepoint.fr/24h-infos/rss.xml')
	print 'Loading dataset...'
	dataset = load_dataset()
	
	print 'Extending dataset'
	print 'Original size: '+str(len(dataset))
	
	for i, entry in enumerate(f['entries']):
		print entry
		text = entry['title'] + ' ' + entry['summary']
		
		if not [(t,r) for (t,r) in dataset if t==text]:	
			print 
			res = raw_input(str(i+1)+' of '+str(len(f['entries']))+' : '+text.strip())
			dataset.append((text, not res))
			print not res
	
	print 'saving new dataset with '+str(len(dataset))+' entries.'
	save_dataset(dataset)
	
def get_nouns(text):
	res = lt.tag_string(text.lower(), lt.SCHEME_LEXICAL_CLASS)
	nouns = [unicode(ss) for tag, ss, range in res if tag=='Noun']
	return nouns
		
def process_dataset(dataset):
	dataset_ext = [(get_nouns(t), c) for t,c in dataset]
	cat = {}
	cat[True] = [(n,c) for n,c in dataset_ext if c]
	cat[False] = [(n,c) for n,c in dataset_ext if not c]

	return cat
	
def classify(cat, text, explain=False):	
	p_true = len(cat[True]) * 1.0/ (len(cat[True]) + len(cat[False]))
	p_false = 1 - p_true
	
	def p_w_cat(w, c):
		w_cat = [(n,c) for (n,c) in cat[c] if w in n]
		return len(w_cat) * 1.0 / len(cat[c])
		
	if explain: print 'p_true: {:>5.1%} p_false: {:>5.1%}'.format(p_true,  p_false)
		
	nouns = get_nouns(text)
	p_t_true = 0.0
	p_t_false = 0.0
	
	for w in nouns:
		p_w_cat_true = p_w_cat(w, True)
		p_w_cat_false = p_w_cat(w, False)
		if explain: print '{0:24s}: {1:>5.1%} {2:>5.1%}'.format(w, p_w_cat_true, p_w_cat_false)
		
		if p_w_cat_true:
			p_t_true = p_t_true + math.log10(p_w_cat_true)
		if p_w_cat_false:
			p_t_false = p_t_false + math.log10(p_w_cat_false)
			
		p_t_true = p_t_true + math.log10(p_true)
		p_t_false = p_t_false + math.log10(p_false)
		
	prediction = math.pow(p_t_true,10) > math.pow(p_t_false,10)
		
	if explain: print 'Prediction: ' + str(prediction)
	if prediction:
		return math.pow(p_t_true,10)
	else:
		return False
	
def test_dataset():
	print
	print 'Initializing...'
	dataset = load_dataset()
	cat = process_dataset(dataset)
	
	print 'Loading feed...'
	f = feedparser.parse('http://rss.liberation.fr/rss/9/')
	print
	print 'Positives:'
	
	def get_classification(entry):
		text = entry['title'] + ' ' + entry['summary']
		text = text.partition('.')[0] # it probably only works for liberation feed...
																	# lt gets crazy when you feed it html
																	# TODO: find another solution
		return (classify(cat, text), text, entry)
		
	def get_key(csf):
		(cs,t,e) = csf
		return cs
	
	classified = [get_classification(entry) for entry in f['entries'] if get_classification(entry)[0]]
	sorted_classified = sorted(classified, key=get_key,reverse=True )
	
	for i, classification in enumerate(sorted_classified):
		(cs, text, entry) = classification
		
		print '{0})'.format(i+1),
		print_link(text, entry['links'][0]['href'])
		print '[ ',
		print_link('explain', 'pythonista://recNews/main?'+urllib.urlencode(
		                                                       [('action', 'run'),
		                                                        ('argv', 'explain'), 
		                                                        ('argv',text)]))
		print ']'
		print
		print

def explain(text):
	print
	print 'Initializing...'
	dataset = load_dataset()
	cat = process_dataset(dataset)
	classify(cat, text, explain=True)
	
def show_menu():
	print
	print 'Menu'
	print '===='
	print
	print '1) Train classifier'
	print '2) Test dataset'
	choice = raw_input(': ')
	print
	
	if choice == '1':
		build_training_set()
	else:
		test_dataset()

if len(sys.argv)==1:
	show_menu()
else:
	cmd = sys.argv[1]
	if cmd == 'showNews':
		test_dataset()
	elif cmd == 'explain':
		s = string.replace(sys.argv[2], '+', ' ') # TODO why doesn't it unpack these strings correctly?
		explain(s)
