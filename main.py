# based on https://www.bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

import feedparser
import linguistictagger as lt
import pickle
import math

def build_training_set():
	f = feedparser.parse('http://www.lepoint.fr/24h-infos/rss.xml')
	dataset = []
	
	for i, entry in enumerate(f['entries']):
		print entry
		text = entry['summary'] or entry['title']
		
		res = raw_input(str(i+1)+' of '+str(len(f['entries']))+' : '+text)
		dataset.append((text, not res))
		
		print not res
		
	# TODO merge datasets
	with open('dataset', 'wb') as g:
		pickle.dump(dataset,g)

# add text parameter		
def classify():
	dataset = []
	with open('dataset', 'rb') as g:
		dataset = pickle.load(g)
	
	def get_nouns(text):
		res = lt.tag_string(text, lt.SCHEME_LEXICAL_CLASS)
		nouns = [unicode(ss) for tag, ss, range in res if tag=='Noun']
		return nouns
		
	dataset_ext = [(get_nouns(text), classe) for text,classe in dataset]
	cat = {}
	cat[True] = [(n,c) for n,c in dataset_ext if c]
	cat[False] = [(n,c) for n,c in dataset_ext if not c]
	
	p_true = len(cat[True]) * 1.0/ len(dataset_ext)
	p_false = 1 - p_true
	
	def p_w_cat(w, c):
		w_cat = [(n,c) for (n,c) in cat[c] if w in n]
		return len(w_cat) * 1.0 / len(cat[c])
		
	print 'p_true: ', p_true, 'p_false: ', p_false
	
	for t,c in dataset:
		print t, c
		
		nouns = get_nouns(t)
		p_t_true = 0.0
		p_t_false = 0.0
		for w in nouns:
			p_w_cat_true = p_w_cat(w, True)
			p_w_cat_false = p_w_cat(w, False)
			print '{0:24s}: {1:>5.1%} {2:>5.1%}'.format(w, p_w_cat_true, p_w_cat_false)
			
			if p_w_cat_true:
				p_t_true = p_t_true + math.log10(p_w_cat_true)
			if p_w_cat_false:
				p_t_false = p_t_false + math.log10(p_w_cat_false)
			
		p_t_true = p_t_true + math.log10(p_true)
		p_t_false = p_t_false + math.log10(p_false)
		
		prediction = math.pow(p_t_true,10) > math.pow(p_t_false,10)
		print 'Prediction: ' + str(prediction)
		if prediction != c: raw_input()
	
	
classify()

