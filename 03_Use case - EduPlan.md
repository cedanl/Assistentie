# 001 | Use case - EduPlan

_Een use case beschrijft hoe een persoon een systeem gebruikt om een specifiek doel te bereiken, inclusief de stappen, alternatieve scenario's en de voorwaarden. Het focust op het "wat" (het doel) in plaats van het "hoe" (de technische implementatie)._

**Aanleiding**
* Digitale assistentie voor **onderwijsprofessionals in het mbo** die werken op strategisch, tactisch of operationeel niveau aan de (door)ontwikkelen van (leven-lang-)lerenden. Waarbij ze continue hun eigen ontwikkeling, die van het vak, het curriculum, de opleiding, het beleid, de sector willen verbeteren ten diensten van de ontwikkeling van de (leven-lang-)lerenden. En daarbij vragen hebben op gebieden als beleidsimpact, toekomstscenario’s, sectorprestaties, instroom/uitstroom/doorstroom, capaciteitsplanning, cohortanalyses, effect interventies, risicosignalering, inspectievragen, groepsinzichten, handelingsadvies, enzovoorts. Er is eerder bij CEDA, in samenwerking met het Mondriaan College, met behulp van studiedata en machine learning-modellen de zogenaamde ‘uitnodigingsregel’ methode ontwikkeld. Deze methode biedt SLB’ers en mentoren een signaleringssysteem waarmee vroegtijdig lerenden op basis van hun uitvalkans kunnen worden opgemerkt.



**Doel**
* Studieloopbaanbegeleiders (SLB’ers), mentoren en mbo‑docenten worden ondersteund bij het zo vroeg mogelijk (binnen de eerste 10 weken van het opleidingsjaar) signaleren van uitvalrisico’s onder hun eerstejaars (leven-lang-)lerende. Op basis van de uitvalprognose plant het systeem automatisch, afhankelijk van beschikbaarheid, een één-op-één voortgangsgesprek in. Om dit (start)gesprek te ondersteunen wordt er tevens een 'EduPlan' gegeneerd die de uitvalprognose op drie elementen toelicht: Afwezigheid in de eerste 10 weken) van het opleidingsjaar, de opleidingsachtergrond van des betreffende (leven-lang-)lerende, plus diens aanmelding geschiedenis. Zodat tijdig besproken kan worden welke ondersteuning nodig is om eventuele uitval – waar mogelijk – te voorkomen.


**Actor(en)**
* Primair: Studieloopbaanbegeleiders (SLB-ers), Mentoren en Docenten in het MBO
* Secundair: (Leven-lang-)lerende in het MBO die dreigen uit te vallen


**Trigger**
* Een (gegenereerde) afspraakverzoek -met EduPlan- naar zowel de primaire als secundaire actoren.


**Preconditions**
* (Leven-lang-)lerende dreigt uit te vallen volgens de ‘Uitnodigingsregel’ ~https://github.com/cedanl/Uitnodigingsregel.
* (Leven-lang-)lerende en SLB-er hebben beide toegang tot dezelfde communicatie- en kantoorsoftware, bijvoorbeeld Proton | Mail, Calender & Meet.


**Postconditions**
* (Leven-lang-)lerende weet wat diens acties zijn om eventuele uitval te voorkomen.
* Gegenereerde gespreksverslag is gemaild naar de SLB-er en de (Leven-lang-)lerende.
* Indien noodzakelijk en gezamenlijk overeengekomen plant het systeem een vervolgafspraak in.


**Basisstroom**
1. De ‘Uitnodigingsregel’ bepaalt welke (Leven-lang-)lerende dreigt uit te vallen.
2. ’EduPlan’ genereert een afspraakverzoek op basis van de voorspelling van de ‘Uitnodigingsregel’.
3. ’EduPlan’ kijkt via contacten wie de SLB-er (of Mentor) is van deze student.
4. ’EduPlan’ verstuurd naar de desbetreffende SLB-er (of Mentor) een e-mail, met een door de AI gegenereerd, persoonlijk EduPlan voor de desbetreffende (Leven-lang-)lerende en gesprekstechnieken voor de SLB-er (of Mentor) om dit gesprek aan te gaan.
5. ’EduPlan’ verstuurd naar beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online videoafspraak.
6. ’EduPlan’ neemt bij goedkeuring van beide aanwezigen het gesprek op.
7. ’EduPlan’ genereert aan het einde van de afspraak een samenvatting van het gesprek.
8. ’EduPlan’ verstuurt naar de SLB-er en de Lerende een mail met daarin de samenvatting van het gesprek.
9. ’EduPlan’ verstuurd met instemming van beide op het eerst mogelijke beschikbare moment een uitnodiging voor een online vervolg (check-in) videoafspraak.
10. Use case herhaalt zich vanaf stap 5 van de 'Basisstroom' tot beide tevreden zijn over de situatie en er geen dreiging tot mogelijke uitval meer is, of herhaalt zich vanaf stap 1 wanneer de (Leven-lang-)lerende  -op een ander moment- nogmaals dreigt uit te vallen.



**Alternatieve stromen**

A1 – Het (voortgangs)gesprek wordt NIET opgenomen
1. Use case gaat verder bij stap 9 van de'Basisstroom'.

F2 – … …



**Foutstromen**

F1 – Lerende is (nog) niet gekoppeld aan een SLB-er

1. De assisitent 'EduPlan' kiest zelf uit de beschikbare SLB-ers een begeleider voor de Lerende.
2. Use case gaat verder bij stap 4 van de'Basisstroom'.

F2 – … …


**Business rules**
* Lerende is aangemeld bij CAMBO (en DUO).
* Lerende is ingeschreven bij de desbetreffende mbo instelling.
* SLB-er hoeft GEEN docentbevoegdheid te hebben.
