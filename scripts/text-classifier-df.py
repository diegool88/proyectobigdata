
from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob
from textblob.exceptions import *

train = [
	('La ciudad tiene mucha inseguridad','seg'),
	('Bandas de ladrones asaltando en el sector centro de la ciudad','seg'),
	('Delincuencia en todas partes de Quito','seg'),
	('Menores de edad robando en las calles principales de la ciudad','seg'),
	('Se vende droga a plena luz del dia','seg'),
	('Estan entrando a las casas a robar electrodomesticos','seg'),
	('Se estan robando los carros','seg'),
	('Crimen y asaltos en todas partes','seg'),
	('La policia es muy ineficiente no se tiene seguridad','seg'),
	('Todas las denuncias quedan en la impunidad','seg'),
	('El trafico es terrible a esta hora','tra'),
	('Estoy estancado en el trafico','tra'),
	('La fila de autos es interminable','tra'),
	('Los semaforos no estan funcionando','tra'),
	('En hora pico el trafico no avanza nada','tra'),
	('Las calles en el sector estan con muchos baches','obr'),
	('Las lluvias han afectado las calles, muchos huecos, no se puede transitar','obr'),
	('Los parques estan maltrados, no existe un buen mantenimiento de las areas verdes','obr'),
	('No tenemos un buen paso peatonal en el sector, los autos cruzan demasiado rapido','obr'),
	('Nadie es capaz de reparar la acera','obr'),
	('Es imposible circular por esta calle','obr')
]

test = [
	('Muchos huecos en las vias al valle de los chillos','obr'),
	('El parque esta descuidado, no cuidan las areas verdes','obr'),
	('Imposible circular por la via interoceanica, existe demasiado trafico','tra')
]

translated_sentences = [(str(TextBlob(sentence).translate(to='en')), category) for (sentence, category) in train]

cl = NaiveBayesClassifier(translated_sentences)

for (sentence, category) in test:
	translation = TextBlob(sentence)
	print '=================================================='
	print 'Oracion Espanol: ' + sentence + '\nOracion Ingles: ' + str(translation.translate(to='en')) + '\nCategoria: ' + category + '\nCategoria Adivinada: ' + str(cl.classify(str(translation.translate(to='en'))))
	print '=================================================='

print 'Exactitud: ' + str(cl.accuracy(test))