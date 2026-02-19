# 001 | Use case - EduPulse

_Een use case beschrijft hoe een persoon een systeem gebruikt om een specifiek doel te bereiken, inclusief de stappen, alternatieve scenario's en de voorwaarden. Het focust op het "wat" (het doel) in plaats van het "hoe" (de technische implementatie)._


**Aanleiding**
* Er is eerder bij CEDA, in samenwerking met het Mondriaan College, met behulp van studiedata en machine learning-modellen de zogenaamde ‘uitnodigingsregel’ methode ontwikkeld. Deze methode biedt SLB’ers en mentoren een signaleringssysteem waarmee vroegtijdig studenten op basis van hun uitvalkans kunnen worden opgemerkt.


**Doel**
* Studieloopbaanbegeleider (SLB-er), mentoren, docenten in het mbo helpen om, op basis van een uitvalprognose van de lerenden die onder hun verantwoordelijkheid vallen, zo vroeg mogelijk uitvalrisico te signaleren en daarop te acteren door op basis van beschikbaarheid automatisch een één-op-één voortgangsgesprek in te plannen. Tijdens dit gesprek wordt er
samen gekeken naar de mogelijke oorzaken van het verwachte uitval, en wordt aan de hand van een, door de Assistent opgesteld, actieplan besproken op welke wijze uitval -indien mogelijk- kan worden voorkomen.


**Actor(en)**
* Primair: Studieloopbaanbegeleiders (SLB-ers), Mentoren en Docenten in het MBO  
* Secundair: Studenten in het MBO die dreigen uit te vallen


**Trigger**
* Een (gegenereerde) afspraakverzoek naar zowel de primaire als secundaire actoren. Toegevoegd: Concept Actieplan voor de SLB-er/Mentor/Docent (student?)


**Preconditions** 
* Student dreigt uit te vallen volgens de ‘Uitnodigingsregel’ ~https://github.com/cedanl/Uitnodigingsregel.
* Student is gekoppeld aan een SLB-er. (@Edwin Elke student is gekoppeld aan een mentor, misschien daar op richten?)
* Student en SLB-er hebben beide toegang tot dezelfde communicatie- en kantoorsoftware: Proton | Mail, Calender & Meet. @Edwin: in eerste instantie focussen op Outlook? Daarom pak je de grootste groep MBO instellingen, daar praktisch alle instellingen met O365 werken. 


**Postconditions**
* Student weet wat diens acties zijn om uitval te voorkomen.
* Gespreksverslag met de actiepunten is gemaild naar de SLB-er en de Student. Eventueel kunnen we, en zo de ontzorging benadrukken, dit gespreksverslag automatisch door een Agent laten maken. Door met Mobiel gesprek op te nemen (of we moeten een ProActAssist apparaatje ontwikkelen :-)), en naar de Assistent te sturen, waarna automatisch transcriptie en gesprekverslag, veilig, wordt gemaakt.    


**Basisstroom**
1. De ‘Uitnodigingsregel’ bepaalt welke Student dreigt uit te vallen.
2. De ’EduPulse’ genereert een afspraakverzoek op basis van de voorspelling van de ‘Uitnodigingsregel’.
3. De ’EduPulse’ kijkt via contacten wie de SLB-er (of Mentor) is van deze student.
4. De ‘EduPulse’ verstuurd naar de desbetreffende SLB-er (of Mentor) een e-mail met een, door de AI gegenereert, persoonlijk actieplan op maat voor de desbetreffende Student en gesprekstechnieken om dit gesprek aan te gaan.
5. De ‘EduPulse’ verstuurd naar beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online videoafspraak.
6. De ‘EduPulse’ neemt bij goedkeuring van beide aanwezigen het gesprek op.
7. De ‘EduPulse’ genereert aan het einde van de afspraak een samenvatting van het gesprek.
8. De 'EduPulse' verstuurt naar de SLB-er en de Lerende een mail met daarin de samenvatting van het gesprek en het actieplan.
9. De ‘EduPulse’ verstuurd met instemming van beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online vervolg (check-in) videoafspraak.
10. Use case herhaalt zich vanaf stap 5 van de 'Basisstroom' tot beide tevreden zijn over de opvolging van het actieplan, of herhaalt zich vanaf stap 1 wanneer de Lerende -op een ander moment- nogmaals dreigt uit te vallen.




**Alternatieve stromen**
A1 – Het (voortgangs)gesprek wordt NIET opgenomen
1. De 'EduPulse' verstuurt naar de SLB-er en de Lerende een mail met daarin alleen het actieplan.
2. Use case gaat verder bij stap 9 van de'Basisstroom'.

A2 – …
…


**Foutstromen / uitzonderingen**
F1 – Lerende is (nog) niet gekoppeld aan een SLB-er
1. De ‘EduPulse’ kiest zelf uit de beschikbare SLB-ers een begeleider voor de Lerende.
2. Use case gaat verder bij stap 4 van de'Basisstroom'.

F2 – …
…



**Business rules**
* Lerende is aangemeld bij CAMBO (en DUO).
* Lerende is ingeschreven bij de desbetreffende mbo instelling.
* SLB-er hoeft GEEN docentbevoegdheid te hebben.



