## Aanpassingen Edupulse

## Situatie 

Gebruik de data en het voorspel model van de Uitnodigingsregel

De twee systemen hebben een fundamenteel ander feature-schema: 

| Aspect 	 | EduPulse (huidig) 							| Uitnodigingsregel  |
| ------	 | ------------	 								| ------------       |
| Features 	 | 4 (Cijfer, Aanwezigheid, EC, Waarschuwingen) | 28 (leeftijd, vooropleiding, sector, verzuim, etc.)
| Model type | RandomForest classifier (.predict\_proba()) 	| 3 regressors (.predict() → continue score) 		   
| Opslag 	 | .pkl 										| .joblib 											   		
| Output 	 | Binair (0/1) met drempel 0.35 				| Continue risicoscore → ranking 					  │ 

## Voorstel: 
- minimale integratie 
- Omdat we zo min mogelijk code willen overnemen heb ik: 
	- Alleen het bestand models/random\_forest\_regressor.joblib gebruikt (of het .joblib van onze voorkeur) 
	- De synthetische data data/raw/synth\_data\_train.csv en synth\_data\_pred.csv als basis gebruikt voor shared/data.csv 
	
Wat ik zelf heb moeten aanpassen in EduPulse: 
1. backend/main.py 
	
	- Vervangen van het StudentData Pydantic model met de 28 features van Uitnodigingsregel. 
	
	- Gebruiken van joblib.load() in plaats van pickle.load(). 
	
	- Gebruiken van .predict() i.p.v. .predict\_proba(), en het gebruiken van de continue score als risicomaat (staat voor nu op 0 later bijv. drempel op 0.5 of percentiel-gebaseerd). 

2. shared/data.csv 
	- Vervangen met de synthetische data van Uitnodigingsregel (of straks echte data als we die hebben). 
	- Kolommen Aanwezigheid, SHAP-features etc. worden dan de Uitnodigingsregel-kolommen. 

3. frontend/app.py 
	- Aanpassen van de filters en tabelkolommen op de Uitnodigingsregel features (StudentAge, absence\_unauthorized, sector-kolommen etc.). 
	
	Wat ik NIET nodig heb gehad (alle Uitnodigingsregel-code):
	
		- module/dataset.py 
		— pandas direct aanroepen 
		- module/features.py 
		— model verwacht al encoded data 
		- module/modeling/train.py / predict.py 
		— gewoon model.predict(X) aanroepen 
		- config.yaml, main.py van Uitnodigingsregel 

Kanttekening: SHAP SHAP werkt prima met RandomForestRegressor — heb ik niets voor aan te hoeven passen, enkel de TreeExplainer aanroep blijft gelijk.