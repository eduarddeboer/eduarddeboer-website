---
title: '147: ReputatieCoach geïnterviewd. Performance en DNS perikelen. Google verrast en stelt teleur.'
date: '2015-09-24T06:30:27+00:00'
description: '**Vandaag is de podcast weer eens gevuld met een aantal nieuwtjes. Zo heb ik afgelopen week meegemaakt hoe een website bijna ten onder ging aan haar eigen succes, waardoor ik stantepede met een oplossing moest komen.** “Bij de timmerman thuis, piepen de deuren” luidt het gezegde… Dat klopt… Ook ik ben niet perfect, daarover zometeen meer. Google liet eerder deze week telefoonnummers zien in de lokale resultaten, maar haalde ze daarna ook meteen weer weg.'
episode: 147
historical: true
archivePeriod: 2012–2016
transcriptStatus: full
feature: __archive_feature_disabled__
cover: __archive_cover_disabled__
thumbnail: __archive_thumbnail_disabled__
showAuthor: false
showReadingTime: false
showTableOfContents: true
showTaxonomies: false
---

> **Historisch archief.** Deze aflevering verscheen op 24-09-2015 als onderdeel van ReputatieCoaching (2012–2016). De oorspronkelijke tekst is hieronder historisch bewaard. Diensten, contactgegevens, links, tools en adviezen kunnen inmiddels verouderd zijn.

{{< audio src="https://archive.org/download/20150924-reputatie-coaching-podcast-147/20150924-ReputatieCoaching-Podcast-147.mp3" title="ReputatieCoaching Podcast #147" >}}

**Transcriptiestatus:** Volledige transcriptie uit het oorspronkelijke archief.

\*\*[*Historische afbeelding niet beschikbaar: ReputatieCoaching Podcast*](https://www.reputatiecoaching.nl/wp-content/uploads/2012/12/Reputatie-Coaching-Podcast-logo-200x200.jpg)Vandaag is de podcast weer eens gevuld met een aantal nieuwtjes. Zo heb ik afgelopen week meegemaakt hoe een website bijna ten onder ging aan haar eigen succes, waardoor ik stantepede met een oplossing moest komen.\*\*

**“Bij de timmerman thuis, piepen de deuren” luidt het gezegde… Dat klopt… Ook ik ben niet perfect, daarover zometeen meer.**

**Google liet eerder deze week telefoonnummers zien in de lokale resultaten, maar haalde ze daarna ook meteen weer weg.**

**Instagram is de 400 miljoen gebruikers gepasseerd en laat daarmee Twitter steeds verder achter zich.**

**Ik sluit de podcast van vandaag af met de opname van een interview met mij! Ja, een paar weken geleden ben ik geïnterviewd en wel door de website “patientenreview.nl”.**

Hallo en hartelijk welkom bij deze aflevering van de ReputatieCoaching Podcast. Ik ben Eduard de Boer, ReputatieCoach. Dit is dé podcast die jou helpt om meer business te genereren, doordat jouw website beter gevonden wordt, zowel lokaal als landelijk en doordat ik je uitleg hoe je je online reputatie kunt verbeteren. Dit alles helpt je om je bedrijf en jezelf beter op de online kaart te plaatsen.

De podcast kun je vinden op [www.reputatiecoaching.nl/147](https://www.reputatiecoaching.nl/147/). Daar vind je niet alleen de tekst, maar ook video’s waar ik het in deze uitzending over heb, alsmede afbeeldingen, links enzovoorts. Bovendien is de podcast te beluisteren in [iTunes](https://www.reputatiecoaching.nl/itunes), op [Stitcher](https://www.reputatiecoaching.nl/stitcher) en ook op [TuneIn Radio](http://tunein.com/radio/ReputatieCoaching-Podcast-p655084/). Ik raad je aan om je op één van die drie kanalen te abonneren op de podcast, zodat je geen aflevering hoeft te missen!

Laat ik dan nu overgaan op de onderwerpen voor vandaag…

## Webserver ten onder aan succes van 1 website!

Ooit had ik een dedicated webserver in een datacenter in Rotterdam. Dat werd me iets te duur en ik ging zoeken naar een goedkopere oplossing voor het hosten van websites. Die had ik al vrij snel gevonden.

Echter, bij de dedicated server had ik nooit een beperking op bandbreedte… Dat wil dus zeggen dat het niet uitmaakte hoeveel dataverkeer de websites bij elkaar opsoupeerden, het bleef gewoon werken. Maar dat is in mijn huidige oplossing niet meer zo…

En daar kwam ik afgelopen week achter. Aarnoud Agricola, voor wie ik ook de website host, had een speciale goochelshow samengesteld en gelanceerd voor de [Kinderboekenweek 2015](http://www.kinderboekenfeestweek.nl). Op zijn website heeft hij hiervoor ook allerlei PDF-bestanden staan, die leerkrachten kunnen downloaden en gebruiken voor het [Kinderboekenweek](http://www.kinderboekenfeestweek.nl)-thema:

En als je dan een beperkte bandbreedte hebt per maand, dan voel je aankomen dat dit problemen geeft. En dat gaf het ook. Vlak nadat hij zijn mailing had verstuurd, kreeg ik al een automatisch mailtje dat het account was “suspended” als gevolg van overmatig bandbreedte gebruik.

Vlak daarna kreeg ik ook een mailtje van Aarnoud zelf, waarin hij me vertelde dat zijn site uit de lucht was.

Ik wilde zijn site niet ongelimiteerde bandbreedte geven, omdat anders alle websites die op hetzelfde systeem staan, niet meer zouden werken. Dus ging ik op zoek naar een andere oplossing.

Als eerste installeerde ik de plugin “W3 Total Cache” op zijn site, om e.e.a. te versnellen. Maar alleen met het versnellen was ik er nog niet. Alle downloads kwamen nog steeds vanaf zijn server, die als een dolle bandbreedte opslurpte en daarmee al mijn overige websites in gevaar bracht.

Daarna stelde ik wat zaken in in “W3 Total Cache” en logde ik in op mijn Amazon AWS account om een zogenaamde Cloudfront distributie te maken voor zijn website. Dat duurde een tergende 25 minuten, terwijl het downloaden als een gek doorging.

Toen was het eindelijk zover en vlogen de tientallen downloads per uur me om de oren, maar die werden simpelweg gehost door Amazon Cloudfront, het Content Delivery Network van Amazon. Daarmee belastten ze dus niet meer mijn website, noch mijn bandbreedte.

Ook alle niet-HTML bestanden, zoals afbeeldingen, Javascript files en stylesheets kwamen vanaf dat moment allemaal vanaf Amazon Cloudfront.

Ik heb het probleem dus kunnen afwenden, voordat het te laat was! Gelukkig!

Maar tjongejonge, het was wel even spannend, kan ik je vertellen!

Ik zat een paar dagen later even te kijken in de statistieken op Cloudfront en zag dat de honderden downloads mij slechts een paar ouderwetse “dubbeltjes” zouden gaan kosten. Nou, die had ik er graag voor over, kan ik je vertellen!

Binnenkort zal ik je eens iets meer hierover uitleggen, over hoe ik het precies heb opgelost.

## DNS records niet goed: “Bij de timmerman thuis, piepen de deuren”

[*Historische afbeelding niet beschikbaar: DNS*](https://www.reputatiecoaching.nl/wp-content/uploads/2015/09/dns.jpg)Jeroen Kooij meldde mij een tijdje geleden al dat reputatiecoaching.nl, dus zonder de ‘www’ niet werkte. Ik had daar nooit bij stilgestaan, omdat Mac OS X volgens mij automatisch probeert een website te benaderen door er zelf ‘www’ voor te zetten, als een gebruiker dat niet doet.

Ik dacht het toen te hebben opgelost, door een “\*” record aan te maken in de DNS. Maar afgelopen week maakte tandarts Dennis mij er op attent, dat de website nog steeds niet werkte, als je er geen ‘www’ voor zette.

Dus dook ik weer de DNS-instellingen in en heb nog een extra zogenaamd “A”-record aangemaakt, dit keer voor een lege hostname op het domein “reputatiecoaching.nl”. Pas toen was het probleem voorgoed opgelost!

Doe hier je voordeel mee en test niet alleen je website op verschillende platformen en besturingssystemen, maar ook mèt en zonder ‘www’ ervoor. Dat voorkomt potentieel verkeerverlies.

Nu maak ik me over verkeerverlies niet echt zorgen, want op dit moment ziet het ernaar uit dat het verkeer deze maand weer met zo’n 20% gegroeid is. OK, de zomermaanden waren iets slapper, maar deze groei is beduidend groter dan de afname in de zomermaanden!

Over groei gesproken: ik kan je meedelen dat ik vorige maand al over het totaal aantal downloads van 2014 ben heengegaan. Het lijkt er dus op, alsof de podcast dit jaar wederom zo’n 2x meer wordt gedownload dan het voorgaande jaar: een trent die zich al een paar jaar voordoet.

## Zo zie je telefoonnummers, en zo zie je ze niet meer!

Vanaf 6 augustus dit jaar zagen veel bedrijven hun verkeer vanaf Google afnemen en dan met name vanuit de lokale zoekresultaten. Per die datum vertoonde Google namelijk niet meer 7 lokale bedrijfsresultaten, maar slechts 3. Bovendien werd het telefoonnummer niet meer rechtstreeks vertoond, noch het volledige adres.

Nu sprong de halve wereld eerder deze week een gat in de lucht, toen opeens de telefoonnummers en de volledige adressen weer verschenen. Maar helaas waren die na een paar dagen weer verdwenen…

We hebben allemaal te vroeg gejuicht…

## Instagram al meer dan 400 gebruikers

[*Historische afbeelding niet beschikbaar: Instagram*](https://www.reputatiecoaching.nl/wp-content/uploads/2015/03/logo-instagram.png)Instagram groeit als kool, en is al geruime tijd het aantal gebruikers van Twitter voorbij gestreefd. Recent liet Instagram weten dat het op dit moment meer dan 400 miljoen actieve gebruikers heeft.

Ik kan je vertellen dat ik ook meer met Instagram doe, dan met Twitter. Twitter lijkt inmiddels gedegradeerd tot een soort van nieuwsticker, waar mensen af en toe op kijken om te zien wat het laatste nieuws is. Van echte interactie tussen mensen of bedrijven en mensen lijkt steeds minder sprake.

Twitter wordt meer en meer een medium om op te “roeptoeteren”…

## Positieve reviews video

En we gaan nog even door met roeptoeteren… Maar dan op het gebied van reviews! Ik vind het namelijk jammer om reviews alleen maar op review sites te laten staan…

Ja, je kunt ze natuurlijk op je website kopiëren en plakken… Maar je kunt er nog meer leuke dingen mee doen! Zo kun je ook screenshots maken en deze in een video verwerken! Ik heb dit al voor verschillende buitenlandse opdrachtgevers gedaan en ik zal komende week ook een voorbeeld maken van reviews van een Nederlandse opdrachtgever.

Dan kun je eens zien wat ik bedoel. Als je de video op de juiste manier uploadt naar YouTube en eventueel andere platformen, dan kan die video ook worden vertoond als mensen je bedrijf zoeken in combinatie met het trefwoord “reviews”, “beoordelingen” of “recensies”.

Maar goed, binnenkort meer hierover…

## ReputatieCoach geïnterviewd

Ik zei het al in de intro: een paar weken geleden ben ik geïnterviewd over reputatie en het belang van reviews en dergelijke. Dat interview wil ik nu graag met je delen…

\*\*Wil je het interview horen? Beluister dan de podcast!\*\*En met dit interview kom ik weer aan het einde van deze podcast.

Als je de podcast en dit soort content leuk vindt, volg me dan via de verschillende kanalen: je kunt me vrijwel overal vinden.

Heb je inderdaad wat aan alle informatie die ik met je deel, help mij dan met het verder verbeteren en promoten van deze podcast. Abonneer je op de podcast, zodat je altijd automatisch de nieuwste uitzending krijgt voorgeschoteld en neem je voor deze week tenminste één andere persoon over de podcast te vertellen. Dat kan een vriend of vriendin zijn, een zakenrelatie, een collega. Het maakt niet uit. Vertel gewoon één persoon over de podcast.

Op de website kun je me een berichtje sturen en zelfs een gratis consult inboeken. Ook kun je me bellen op 084–8831556 en zelfs rechtstreeks op de website een voicemail achterlaten.

Dit was [ReputatieCoaching Podcast aflevering 147](https://www.reputatiecoaching.nl/147/) en mijn naam is [Eduard de Boer](http://nl.linkedin.com/in/eduarddeboer/nl).

Ik wens je de komende week weer succes met het werken aan je reputatie, zodat je meteen je reputatie voor jou kunt laten werken!

Tot volgende week!

Doei!

Links naar content die in deze podcast aan bod komt:

```
  * [ReputatieCoaching Podcast in iTunes](https://www.reputatiecoaching.nl/itunes)
  * [ReputatieCoaching Podcast op Stitcher](https://www.reputatiecoaching.nl/stitcher)
  * [ReputatieCoaching Podcast op TuneIn Radio](http://tunein.com/radio/ReputatieCoaching-Podcast-p655084/)
  * [ReputatieCoaching Podcast RSS-feed](https://feeds.reputatiecoaching.nl/ReputatieCoachingPodcast)
```
