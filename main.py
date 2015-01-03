# based on https://www.bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

import feedparser
import linguistictagger as lt
import pickle
import math

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
	with open('dataset', 'wb') as g:
		pickle.dump(dataset,g)
			
def build_training_set():
	f = feedparser.parse('http://www.lepoint.fr/24h-infos/rss.xml')
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
	
	if explain: print nouns
	
	for w in nouns:
		p_w_cat_true = p_w_cat(w, True)
		p_w_cat_false = p_w_cat(w, False)
		if explain: print '{0:24s}: {1:>5.1%} {2:>5.1%}'.format(w, p_w_cat_true, p_w_cat_false)
		if explain: print 'hi'
		if p_w_cat_true:
			p_t_true = p_t_true + math.log10(p_w_cat_true)
		if p_w_cat_false:
			p_t_false = p_t_false + math.log10(p_w_cat_false)
			
		p_t_true = p_t_true + math.log10(p_true)
		p_t_false = p_t_false + math.log10(p_false)
		
	prediction = math.pow(p_t_true,10) > math.pow(p_t_false,10)
		
	if explain: print 'Prediction: ' + str(prediction)
	return prediction
	
def test_dataset():
	print 'Initializing...'
	dataset = load_dataset()
	cat = process_dataset(dataset)
	
	print 'Loading feed...'
	f = feedparser.parse('http://rss.liberation.fr/rss/9/')
	print 'done'
	print
	
	print 'Positives:'
	for i, entry in enumerate(f['entries']):
		#print entry
		text = entry['title'] + ' ' + entry['summary']
		text = text.partition('.')[0] # it probably only works for liberation feed...
																	# lt gets crazy when you feed it html
																	# TODO: find another solution
		
		if classify(cat, text):
			print '{0})'.format(i+1),
			print_link(text, entry['links'][0]['href'])	
			print
			print

	print 		
	print 'Negatives:'
	for i, entry in enumerate(f['entries']):
		#print entry
		text = entry['title'] + ' ' + entry['summary']
		text = text.partition('.')[0] # it probably only works for liberation feed...
		
		if not classify(cat, text):
			print '{0})'.format(i+1),
			print_link(text, entry['links'][0]['href'])	
			print
			print
			
#classify()
#build_training_set()
test_dataset()

# TODO add explain link close to each result in test using pythonista URL schema
