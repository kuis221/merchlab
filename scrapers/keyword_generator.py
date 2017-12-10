import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

NLTK_STOP_WORDS = stopwords.words('english')
SHORT_STOP_WORDS = [e for e in NLTK_STOP_WORDS if len(e) <= 4]
WORDS_TO_REMOVE = set(SHORT_STOP_WORDS + ["t shirt", "tee shirt", "t-shirt", "tshirt", "shirt"])

def generate_bigrams(input_list):
	if len(input_list) < 2:
		return []
	return [list(e) for e in zip(input_list, input_list[1:])]

def generate_trigrams(input_list):
	if len(input_list) < 3:
		return []
	return [list(e) for e in zip(input_list, input_list[1:], input_list[2:])]

def remove_words_from_input_list(input_list):
	return [e for e in input_list if e.lower() not in WORDS_TO_REMOVE]

def turn_ngrams_into_searches(ngrams):
	searches = []
	for gram in ngrams:
		searches.append(' '.join(gram).strip())
	return searches

def is_floatable_element(possible_float):
	try:
		float(possible_float)
		return True
	except Exception as e:
		return False

def generate_new_searches(title):
	searches = []
	input_list = title.replace(',', '').replace('.', '').split(' ')
	input_list = [e.strip().strip('-').strip('|').strip('&').strip("'").strip(":").strip(')').strip('(').strip().lower() for e in input_list]
	input_list = remove_words_from_input_list(input_list)
	input_list = [e for e in input_list if not is_floatable_element(e)]
	#print("before", input_list)
	bigrams = generate_bigrams(input_list)
	trigrams = generate_trigrams(input_list)
	#print("after", input_list)
	searches = input_list + turn_ngrams_into_searches(bigrams + trigrams)
	return searches

#print generate_new_searches("the ugly dog is fat tshirt")