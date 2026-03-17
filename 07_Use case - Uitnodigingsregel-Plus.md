001 | Use case - Uitnodigingsregel+

Een use case beschrijft hoe een persoon een systeem gebruikt om een specifiek doel te bereiken, inclusief de stappen, alternatieve scenario's en de voorwaarden. Het focust op het "wat" (het doel) in plaats van het "hoe" (de technische implementatie).

**Aanleiding**

Er is eerder bij CEDA, in samenwerking met het Mondriaan College, met behulp van studiedata en machine learning-modellen de zogenaamde ‘uitnodigingsregel’ methode ontwikkeld. Deze methode biedt SLB’ers en mentoren een signaleringssysteem waarmee vroegtijdig lerenden op basis van hun uitvalkans kunnen worden opgemerkt.


**Doel**

Studieloopbaanbegeleiders (SLB’ers), mentoren en mbo‑docenten worden binnen de eerste 10 weken van het opleidingsjaar ondersteund met het zo vroegst mogelijk signaleren van uitvalrisico’s onder de lerenden waarvoor zij verantwoordelijk zijn. Op basis van de uitvalprognose wordt er door de Assistent 'Uitnodigingsregel+' een gespreksplan opgesteld wat gebruikt kan worden tijdens het kennismakingsgesprek om te bespreken op welke wijze uitval – indien mogelijk – kan worden voorkomen.


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

1. De ‘Uitnodigingsregel+’ bepaalt welke Lerende dreigt uit te vallen.
2. De ‘Uitnodigingsregel+’ verstuurd naar de desbetreffende SLB-er (of Mentor) een e-mail met een, door de AI gegenereert, persoonlijk gespreksplan op maat voor de desbetreffende Lerende en gesprekstechnieken om dit gesprek aan te gaan.



**Foutstromen / uitzonderingen**

F1 – Lerende is (nog) niet gekoppeld aan een SLB-er

De ‘Uitnodigingsregel+’ kiest zelf uit de beschikbare SLB-ers een begeleider voor de Lerende.
Use case gaat verder bij stap 2 van de'Basisstroom'.

F2 – … …

**Business rules**
Lerende is aangemeld bij CAMBO (en DUO).
Lerende is ingeschreven bij de desbetreffende mbo instelling.
SLB-er hoeft GEEN docentbevoegdheid te hebben.
