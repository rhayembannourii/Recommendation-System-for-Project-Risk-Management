# PRM-Assist
PMBOK Project Management Body Of Knowledge

The premise of this work is to address the problem of OL that could be applied to text analysis as a
way to build PRM ontology which will be integrated further in an recommendation system that
predict and provide a real time personnalized recommendation. This ontology
will be learnt from an unstructured text which called “ PMBOK + PMI’s standard for PRM” as a
reference guideline that embodies a set of knowledge and recommendations respectively.

1- The automatic knowledge retrieval process from unstructured text which is the
PMBOK 5th (41 pages [from 309 to 354 page]) and PMI’s standard for PRM (116
pages) using NLP techniques (tokenization, Pos tagging, stemming, etc) via NLTK
and SPACY : TF_idf Measure and cosine-similarity 

2- This retrieved knowledge will be parsed following OL layer cake into OWL concepts
, Object/Data properties, axioms ,rules for building “PRM-Onto” by applying
NLP techniques, data mining, and machine learning techniques ( association rules,
ontology pruning, clustering hierarcical technqiue) for structuring ontological
elements via OWLREADY, RDF lib etc…

3- Based on Ontology repository, Recommendations will inferred using the recommendation techniques

4- Implementing an ontology based recommendation system as a web application via
Django framework  to infer a real-time personalized recommendation according to project risk management

