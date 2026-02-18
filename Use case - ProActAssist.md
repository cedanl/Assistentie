# Use case - ProActAssist

_Een use case beschrijft hoe een persoon een systeem gebruikt om een specifiek doel te bereiken, inclusief de stappen, alternatieve scenario's en de voorwaarden. Het focusseert op de "wat" (het doel) in plaats van de "hoe" (de technische implementatie)._


**Doel**
* Studieloopbaanbegeleider (SLB-er) willen op het eerst mogelijke beschikbare moment een één-op-één gesprek met die lerenden die dreigen uit te vallen om met hen een concrete actieplan door te nemen en zo uitval te voorkomen.



**Actor(en)**
* Primair: Studieloopbaanbegeleiders (SLB-ers) in het mbo  
* Secundair: Lerenden (waar de SLB-er verantwoordelijk voor is) die dreigen uit te vallen


**Trigger**
* Een (gegenereerde) afspraakverzoek naar zowel de mentor als de lerende die dreigt uit te vallen.


**Preconditions** 
* Lerende dreigt uit te vallen volgens de ‘Uitnodigingsregel’ ~https://github.com/cedanl/Uitnodigingsregel.
* Lerende is gekoppeld aan een SLB-er.
* Lerende en SLB-er hebben beide toegang tot dezelfde communicatie- en kantoorsoftware: Proton | Mail, Calender & Meet.


**Postconditions**
* Lerende weet wat diens acties zijn om uitval te voorkomen.
* Gespreksverslag met de actiepunten is gemaild naar de SLB-er en de Lerende.


**Basisstroom**
1. De ‘Uitnodigingsregel’ bepaalt welke Lerende dreigt uit te vallen.
2. De ’ProActAssist’ genereert een afspraakverzoek op basis van de voorspelling van de ‘Uitnodigingsregel’.
3. De ’ProActAssist’ kijkt via contacten wie de SLB-er is van deze lerende.
4. De ‘ProActAssist’ verstuurd naar de desbetreffende SLB-er een e-mail met een gegenareert persoonlijk actieplan voor de desbetreffende Lerende en gesprekstechnieken om dit gesprek aan te gaan.
5. De ‘ProActAssist’ verstuurd naar beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online videoafspraak.
6. De ‘ProActAssist’ neemt bij goedkeuring van beide aanwezigen het gesprek op.
7. De ‘ProActAssist’ genereert aan het einde van de afspraak een samenvatting van het gesprek.
8. De 'ProActAssistent' verstuurt naar de SLB-er en de Lerende een mail met daarin de samenvatting van het gesprek en het actieplan.
9. De ‘ProActAssist’ verstuurd met instemming van beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online vervolg (check-in) videoafspraak.
10. Use case herhaalt zich vanaf stap 5 van de 'Basisstroom' tot beide tevreden zijn over de opvolging van het actieplan, of herhaalt zich vanaf stap 1 wanneer de Lerende -op een ander moment- nogmaals dreigt uit te vallen.




**Alternatieve stromen**
A1 – Het (voortgangs)gesprek wordt NIET opgenomen
1. De 'ProActAssistent' verstuurt naar de SLB-er en de Lerende een mail met daarin alleen het actieplan.
2. Use case gaat verder bij stap 9 van de'Basisstroom'.

A2 – …
…


**Foutstromen / uitzonderingen**
F1 – Lerende is (nog) niet gekoppeld aan een SLB-er
1. De ‘ProActAssist’ kiest zelf uit de beschikbare SLB-ers een begeleider voor de Lerende.
2. Use case gaat verder bij stap 4 van de'Basisstroom'.

F2 – …
…



**Business rules**
* Lerende is aangemeld bij CAMBO (en DUO).
* Lerende is ingeschreven bij de desbetreffende mbo instelling.
* SLB-er hoeft GEEN docentbevoegdheid te hebben.



