001 | Use case - EduPlan

Een use case beschrijft hoe een persoon een systeem gebruikt om een specifiek doel te bereiken, inclusief de stappen, alternatieve scenario's en de voorwaarden. Het focust op het "wat" (het doel) in plaats van het "hoe" (de technische implementatie).

**Aanleiding**

Er is eerder bij CEDA, in samenwerking met het Mondriaan College, met behulp van studiedata en machine learning-modellen de zogenaamde ‘uitnodigingsregel’ methode ontwikkeld. Deze methode biedt SLB’ers en mentoren een signaleringssysteem waarmee vroegtijdig lerenden op basis van hun uitvalkans kunnen worden opgemerkt.


**Doel**

Binnen de eerste 10 weken van het opleidingsjaar worden studieloopbaanbegeleiders (SLB'ers), mentoren en mbo‑docenten ondersteund bij het vroegtijdig signaleren van mogelijke uitvalrisico’s onder hun eerstejaars (leven-lang-)lerende. Op basis van de uitvalprognose stelt de Assistent 'EduPlan' een gespreksplan op dat gebruikt kan worden tijdens het StratGesprek, zodat tijdig besproken kan worden welke ondersteuning nodig is om eventuele uitval – waar mogelijk – te voorkomen.


**Actor(en)**

Primair: Studieloopbaanbegeleiders (SLB-ers), Mentoren en Docenten in het MBO

Secundair: (Leven-lang-)lerenden in het MBO die dreigen uit te vallen


**Trigger**

Een op basis van uitvalprognose (gegenereerd) gespreksplan- naar zowel de primaire als secundaire actoren.


**Preconditions**

Lerende dreigt uit te vallen volgens de ‘Uitnodigingsregel’ ~https://github.com/cedanl/Uitnodigingsregel.


**Postconditions**

Lerende weet wat diens acties zijn om uitval te voorkomen.


**Basisstroom**

1. De ‘Uitnodigingsregel’ bepaalt welke Lerende dreigt uit te vallen.
2. De assisitent 'EduPlan' verstuurd naar de desbetreffende SLB-er (of mentor) een e-mail met een, door de AI gegenereert, persoonlijk gespreksplan op maat voor de desbetreffende (leven-lang-)lerende en gesprekstechnieken om dit gesprek aan te gaan.



**Foutstromen / uitzonderingen**

F1 – Lerende is (nog) niet gekoppeld aan een SLB-er

De assisitent 'EduPlan' kiest zelf uit de beschikbare SLB-ers een begeleider voor de Lerende.
Use case gaat verder bij stap 2 van de'Basisstroom'.

F2 – … …

**Business rules**
Lerende is aangemeld bij CAMBO (en DUO).
Lerende is ingeschreven bij de desbetreffende mbo instelling.
SLB-er hoeft GEEN docentbevoegdheid te hebben.
