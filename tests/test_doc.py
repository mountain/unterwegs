from unterwegs.nlp.doc import bow


print(bow('''
What is the best way to add/remove stop words with spacy?
I am using token.is_stop function and would like to make some custom changes to the set. 
I was looking at the documentation but could not find anything regarding of stop words. Thanks!
'''))
