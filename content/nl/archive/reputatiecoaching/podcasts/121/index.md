---
author: Eduard
date: 2015-03-26 12:41:00+00:00
draft: false
title: '121: Serverstoring... Geswitched van SendReach naar Mailchimp. Smush.it stopt
ermee! Belangrijk nieuws over YouTube infokaarten.'
categories:
- Podcasts
tags:
- YouTube

type: reputatiecoaching-podcast
layout: reputatiecoaching-podcast
episode: "121"
archive: true
historical: true
series: "ReputatieCoaching Podcast"
source_url: "https://www.reputatiecoaching.nl/121/"
archive_year: "2015"
---

**![ReputatieCoaching Podcast](/archive/reputatiecoaching/media/wp-content/uploads/2012/12/Reputatie-Coaching-Podcast-logo-200x200.jpg)

Zoals je mogelijk hebt gemerkt is de podcast vandaag iets later uitgekomen, dan om 08:30 uur. Dat kwam door een storing. Ik begin vandaag met nieuws voor de abonnees van de mailinglist, omdat ik ben overgeschakeld van SendReach naar Mailchimp.**

**En herinner je je nog onze slechte ervaringen met de zonnebrandcrème in Spanje? Smush.It stopt ermee en dat is jammer! Waarom? Ik vertel je er zo meer over!**

**Dan heb ik wat nieuwe inzichten ten aanzien van de mobielvriendelijke Google update van 21 april aanstaande en ik sluit de podcast van vandaag af met YouTube infokaarten.**

Hallo en hartelijk welkom bij deze aflevering van de ReputatieCoaching Podcast. Ik ben Eduard de Boer, ReputatieCoach. Dit is dé podcast die jou helpt om meer business te genereren, doordat jouw website beter gevonden wordt, zowel lokaal als landelijk en doordat ik je uitleg hoe je je online reputatie kunt verbeteren. Dit alles helpt je om je bedrijf en jezelf beter op de online kaart te plaatsen.

De podcast van vandaag kun je vinden op [www.reputatiecoaching.nl/121](https://www.reputatiecoaching.nl/121/). Daar vind je niet alleen de tekst, maar ook video’s waar ik het in deze uitzending over heb, alsmede afbeeldingen, links enzovoorts. Bovendien is de podcast te beluisteren in [iTunes](https://www.reputatiecoaching.nl/itunes), op [Stitcher](https://www.reputatiecoaching.nl/stitcher) en op [TuneIn Radio](http://tunein.com/radio/ReputatieCoaching-Podcast-p655084/). Ik raad je aan om je op één van die drie kanalen te abonneren op de podcast, zodat je geen aflevering hoeft te missen!

Laat ik dan nu overgaan op de onderwerpen voor vandaag…

## Storing aan de server: hele woensdag bezig!

Ohhh… Eerst nog even wat anders. Deze podcast kwam niet precies om 08:30 uur live. En dat had een oorzaak… Een oorzaak die mijn volle aandacht en iets meer dan 7 uur opeiste. De dedicated server die ik huur in een datacenter in Rotterdam leek opeens kuren te hebben. Het hebben van een eigen server heeft zo zo’n voor- en nadelen. Een groot voordeel vind ik dat je de server volledig kunt inrichten, zoals je dat zelf wilt. Een nadeel is dat je zelf moet komen opdraven als er problemen zijn. En dat was nu dus het geval.

Ik had de indruk dat alle websites die ik op die server draai steeds langzamer werden. Waar ik trouwens heel benieuwd naar ben, is of jij als bezoeker van www.reputatiecoaching.nl de afgelopen paar weken net als ik de idee had dat het wat langer duurde voordat de pagina’s werden vertoond. Heb je iets gemerkt, laat het me alsjeblieft weten en stuur een mailtje naar [podcast@reputatiecoaching.nl](mailto:podcast@reputatiecoaching.nl) met je bevindingen.

Welnu, mijn gevoel werd bevestigd toen ik eens in Google Webmaster Tools ging kijken naar de Crawlstatistieken voor de ReputatieCoaching website. Daar zag ik dat er iets veranderd leek te zijn sinds 8 maart 2015. Want vanaf die tijd steeg de gemiddelde laadtijd van de pagina’s op de site van zo’n 800 milliseconden naar 2,9 seconden…

[![Google Webmaster Tools crawlstatistieken](https://lh6.googleusercontent.com/-XWyQL4b9rEg/VRP_Sy4ZUvI/AAAAAAAAB5Q/ZmLuZUn5TO0/w920-h782-no/20150325-Webmaster-Tools-Crawlstats.png)

](https://lh6.googleusercontent.com/-XWyQL4b9rEg/VRP_Sy4ZUvI/AAAAAAAAB5Q/ZmLuZUn5TO0/w920-h782-no/20150325-Webmaster-Tools-Crawlstats.png)

Ook de laadtijd op de site van Allround Fotografie, die op dezelfde server draait, nam toe van zo’n 500 milliseconden per pagina op 8 maart tot meer dan anderhalve seconde op 23 maart jongstleden.

In beide gevallen spreek je dus over een verdrievoudiging en dat is nogal een stijging! Ik vond dat teveel en dook er dus vol in! Bij Windows had je gewoon het systeem opnieuw opgestart, maar dat probeer ik altijd zo lang mogelijk uit te stellen. Om dat te illustreren, moet je maar eens de screenshot in de show notes bekijken:

![Uptime webserver](https://lh4.googleusercontent.com/-RqjqDYWVUzs/VRP_3ioeSvI/AAAAAAAAB5w/ZOTj7gZFIaE/w557-h155-no/20150326-uptime-server.png)

Daarin kun je zien dat de server al meer dan 840 dagen up is. Dat wil dus zeggen dat de server al die tijd draait en dus nooit tussentijds is ge-reboot. Want dan begint de teller immers weer op 0.

Anyway, het kostte me een aantal uren experimenteren en testen. In de tussentijd moest ik af en toe de webserver herstarten. Dus mocht je gisteren wat onregelmatigheden hebben bespreurd op de site, dan begrijp je nu dus wat daar de oorzaak van was.

Vrijwel alle sites bleken vlak na 8 maart langzamer te zijn gaan laden. Hoewel ik toch redelijk goed bijhoud als ik significante veranderingen aan de server doorvoer, kon ik die niet herleiden tot een bepaalde actie van mijzelf. Maar aan de andere kant ben ik me er van bewust dat over het algemeen software niet uit zichzelf anders gaat functioneren…

Ik wil niet te technisch worden, want dat is niet het doel van deze podcast, maar uiteindelijk heb ik wat instellingen aan de configuratie van de server veranderd, waardoor sommige processen niet te lang bleven draaien, maar binnen een afzienbare tijd stopten en opnieuw opstartten. Vlak voor het avondeten had ik alles naar behoren werkend en na het avondeten heb ik nog wat verdere optimalisaties doorgevoerd.

De komende dagen houd ik de server nauwlettend in de gaten om te zien of het nu goed blijft gaan.

Wat kunnen we hiervan leren? Allereerst moet je niet te snel genoegen nemen met iets een tragere website, als je weet dat die normaal sneller is. En dan moet je gaan zoeken… Daarvoor gebruikte ik Google Webmaster Tools, een gratis service van Google. En gelukkig gebruik ik die al lange tijd, waardoor ik tot drie maanden terug kan kijken. Daardoor kon ik zien dat het probleem vlak na 8 maart was ontstaan. In de grafiek zag ik dat de laadtijd voor alle sites langer was geworden. Het was dus niet de configuratie van een enkele website, waarop een verkeerde plugin draaide.

Ik denk dat voor jou het belangrijkste leerpunt hiervan is dat je [Google Webmaster Tools](https://www.google.com/webmasters/tools/) moet activeren voor je site c.q. voor al je sites. Want ook als Google je site een handmatige penalty geeft of andere problemen aantreft, dan krijg je dat alleen daar te horen.

En als slagroom op de koffie is het nuttig en wellicht handig voor je om te weten dat je in Google Webmaster Tools nog een goed beeld kunt krijgen van de trefwoorden waar je op rankt en op welke gemiddelde positie je ermee scoort in de zoekresultaten. Want in Google Analytics zie je die gemiddelde ranking van de zoektermen niet meer.

Tot zover over de storing op de server en het nut van Google Webmaster Tools.

## Ik lees WhatsApp alleen nog maar om 09:30, 16:30 en 20:30 uur

Nog even iets, voor ik de onderwerpen van vandaag behandel. Ik had je verteld dat ik op persoonlijke titel ben [gestopt met Facebook](https://www.reputatiecoaching.nl/118/). Eén van de redenen was de hoeveelheid tijd die het me kostte, wat in geen vergelijking stond met het rendement zoals ik dat ervoer. Ik voel me nog steeds comfortabel bij die keuze en ik mis Facebook geen moment.

Om mij nog beter te kunnen concentreren op mijn werkzaamheden ben ik nog een stap verder gegaan. WhatsApp was voor mij een grote bron van irritatie vanwege de verstoring die het veroorzaakte bij elk ontvangen berichtje. 99,99% van die instantberichten was helemaal niet tijdkritisch en veelal irrelevant, ongewenst, niet interessant en dus feitelijk bandbreedtevervuiling. Maar het ergste vond ik dat ik elke keer weer uit mijn concentratie werd gehaald en om vervolgens weer in de “flow” te komen had ik dan tot overmaat van ramp steeds zo’n 15–20 minuten nodig. Pure tijdverspilling!

Dus heb ik alle notificaties uitgezet. Als ik een WhatsApp bericht ontvang klinkt er geen piepje en zie ik geen pushnotificatie in mijn scherm. Ik heb in mijn iPhone 3 alarmen gezet: eentje om 09:30 uur, eentje om 16:30 en eentje om halfnegen ’s avonds. Op die momenten open ik WhatsApp en handel ik de berichten af.

Om dit naar de buitenwereld duidelijk te maken heb ik dit in mijn status in WhatsApp vermeld. Hopelijk lezen mensen het. Anders merken ze het vanzelf. Want laten we eerlijk zijn: de meeste communicatie is niet zo tijdkritisch en kan prima op een later moment plaatsvinden.

Dan nu echt de onderwerpen voor vandaag!

## Overstap SendReach naar Mailchimp voor mailinglist

![mailchimp-logo](/archive/reputatiecoaching/media/wp-content/uploads/2015/03/mailchimp-logo.png)

Dankzij de plugin SumoMe, waar ik het in [podcast 120](https://www.reputatiecoaching.nl/120/) over had, groeit mijn mailinglist nu vele malen sneller dan voorheen. De groei is nog steeds zo’n 5x groter dan voorheen, dus dat loopt prima! Nu moet je weten dat ik tot zo’n anderhalf tot twee jaar geleden altijd een trouw gebruiker was van Mailchimp. Dat voldeed meer dan voldoende aan al mijn eisen.

Maar twee jaar geleden was ik veel zoekende naar wat de Amerikan noemen “The Next Shiny Object”. In die tijd was ik wat minder kritisch en had de illusie dat al die mooie tooltjes die Internet marketeers en affiliates aanprezen mij konden helpen om sneller meer resultaat te behalen. Dat heeft de nodige Euro’s gekost aan achteraf beschouwd zinloze programma’s, plugins, tools en andere zinloze zaken.

Zoals ik al zei, gebruikte ik toen nog steeds Mailchimp en opeens kwam er iets tevoorschijn dat nóg mooier leek te zijn, met de welklinkende naam “SendReach”. Dat beloofde fantastische resultaten, waar ik nu even niet verder op in wil gaan omwille van de tijd en om een beetje on-topic te blijven. Kort gezegd komt het erop neer dat ik voor een significant maar gelukkig eenmalig bedrag toegang tot de service heb gekocht.

De mailinglist van ReputatieCoaching heb ik initieel hierin opgebouwd. Maar het begon te wringen: er kwamen maar geen nieuwe features bij in SendReach en nu er een nieuwe versie was uitgebracht moesten alle uitgaande mails opeens gecontroleerd worden door het bedrijf. Het was vooral dit, wat mij tegen de borst stuitte. Want als ik een mail wil versturen, wil ik niet moeten wachten op een organisatie die mogelijk in een heel andere tijdzone zit en zelfs in het weekend geen mails goedkeurt.

Dus heb ik mijn account in Mailchimp afgestoft en opgepoetst. Daarna heb ik alle gegevens uit SendReach geëxporteerd en in mijn account in Mailchimp geïmporteerd. Dat was eergisteren en vanaf deze week verstuur ik de mails dus weer vanuit de oude, vertrouwde Mailchimp omgeving.

## Vision zonnebrandcrème ervaringen

Tijdens de zomervakantie in Spanje in 2014 hadden we een [slechte ervaring met Vision zonnebrandcrème](https://www.reputatiecoaching.nl/88/). Ik heb daar toen een korte video van gemaakt en die op YouTube gezet. Voor het geval je die nog nooit hebt gezien, heb ik ’m nog even opgenomen in de show notes van deze podcast, op [www.reputatiecoaching.nl/121](https://www.reputatiecoaching.nl/121/):

[Historische video op YouTube](https://www.youtube.com/watch?v=ALrgla7oYxA)

In reactie op mijn mail naar de importeur Vemedia kreeg ik een nette mail terug, die ik in [podcast 96](https://www.reputatiecoaching.nl/96/) heb behandeld. Daarin schreef Anita de Haan, Coördinator Consumentenservice van Vemedia dat begin 2015 de samenstelling zou veranderen en het bedrijf mij dan met alle plezier een nieuwe tube zou opsturen.

Inmiddels heb ik vorige week contact gezocht met Vemedia om te vragen of ik de nieuwe tube kon ontvangen om die te testen. Daarop ontving ik binnen een dag het antwoord:

<blockquote>Beste meneer De Boer,

Hartelijk dank voor uw reactie.

Wij willen u graag twee nieuwe tubes toesturen van de Vision voor uw gezin, charge 2015, zonder bittere smaak. Wij komen u graag tegemoet in het ongemak en betreuren het zeer dat u allevier verbrand bent vorig jaar.

Laat u ons nog even weten naar welke factor uw voorkeur uitgaat?

Wij zien u reactie graag tegemoet en wensen u alvast een hele fijne zomer toe met onze Vision!

Met vriendelijke groet, Kind regards, Mit freundlichen Grüssen, Salutations distinguées,

Anita de Haan

Coördinator Consumentenservice</blockquote>

Komend zomer gaan we net als vorig jaar naar Spanje en naar dezelfde regio. Dus ik ben in staat een representatieve vergelijking te doen om te onderzoeken of de samenstelling veranderd is en of die nu wel goed werkt.

Dat hoor je na de zomervakantie!

## Webinars met gebruikersvragen

![Webinar Internetmarketing voor Fotografen](/archive/reputatiecoaching/media/wp-content/uploads/2014/12/Webinar.png)

Er zijn al enkele vragen binnengekomen om te behandelen in een webinar / online workshop. Daar ga ik dus de komende tijd mee aan de slag. Maar er is nog ruimte voor meer vragen. Dus: stuur ze je vragen naar [podcast@reputatiecoaching.nl](mailto:podcast@reputatiecoaching.nl).

Vorige week stelde ik voor om WordPress plugins te behandelen, maar dat is natuurlijk geen beperking! Als je andere vragen of problemen hebt, die je graag eens wat uitvoeriger behandeld wilt zien, laat het me dan weten.

Ik ga nog even door met het verzamelen van vragen en onderwerpen, om zo een aantal webinars achter elkaar te kunnen behandelen.

## Smush.it stopt ermee… Helaas! Jammer!

Jarenlang heb ik dankbaar gebruik gemaakt van Smush.it, een service van Yahoo, waarmee je de bestandsomvang van afbeeldingen en foto’s kon verkleinen, zonder zichtbaar kwaliteitsverlies. Ik had daarom in de meeste WordPress sites de Smush.it-plugin geïnstalleerd. Daardoor werden alle afbeeldingen die ik in die sites uploadde, automatisch geoptimaliseerd.

Maar eerder deze week kwam er een nieuwe versie van de plugin uit. Die vertoonde een melding in het WordPress dashboard, waarin werd aangekondigd dat Yahoo stopt met de gratis versie van Smush.it of mogelijk er de stekker helemaal uittrekt:

[![Smush.it stopt ermee!](https://lh4.googleusercontent.com/-7UAJEzBEE3I/VRP_SxIIWdI/AAAAAAAAB5k/wyl02Ty2Vnw/w986-h210-no/20150323-Exit-Smushit.png)

](https://lh4.googleusercontent.com/-7UAJEzBEE3I/VRP_SxIIWdI/AAAAAAAAB5k/wyl02Ty2Vnw/w986-h210-no/20150323-Exit-Smushit.png)

Dus heb ik meteen in alle WordPress sites die ik manage de plugin verwijderd.

Een tijdje geleden heb ik een instructievideo gemaakt over de [bestandsgrootte van een foto verkleinen op Mac, PC en Linux](https://www.youtube.com/watch?v=TKCTXegNy80) met compressor.io:

[Historische video op YouTube](https://www.youtube.com/watch?v=TKCTXegNy80)

Sinds ik compressor.io heb leren kennen optimaliseer ik de afbeeldingen steeds handmatig, voordat ik ze upload. En qua hoeveelheid extra werk valt dat best mee. Ik denk dat het per podcast minder dan 5 minuten extra tijd kost.

Vertel eens: wat doe jij? Upload jij plompverloren alle afbeeldingen naar je WordPress-site? Of heb jij ook een optimalisatieplugin draaien? Welke gebruik jij? Of gebruik je net als ik handmatig een online service als compressor.io? Laat het me weten onderaan de show notes van deze podcast, op [www.reputatiecoaching.nl/121](https://www.reputatiecoaching.nl/121/).

## Korte update over mobile friendly algoritme update van 21 april a.s.

Als je als webmaster nog niet hebt gehoord van de mega-update in Google die ons staat te wachten per 21 april, dan moet je echt vaker naar deze podcast luisteren of iets meer het nieuws van de zoekmachines volgen. Dit is namelijk een update die alle mobielonvriendelijke websites raakt, wereldwijd in alle talen, zij het dan “alleen” in de mobiele zoekresultaten.

Google heeft namelijk bekendgemaakt dat een mobielvriendelijke essentieel is voor het hoger scoren in de mobiele zoekresultaten. Met andere woorden: websites die mobielvriendelijk zijn gaan per 21 april hoger scoren dan sites die niet goed te bekijken zijn op mobiele apparaten, zoals smartphones.

Inmiddels is er wat meer informatie losgekomen van Google over dit onderwerp. De highlights daarvan zal ik je geven:

* Het algoritme is per 21 april a.s. operationeel, maar het zal enige dagen tot een week duren totdat het effect en de impact ervan wereldwijd en in alle talen zichtbaar is.

* Je website is _wèl_ mobielvriendelijk, of _niet_. Er zijn geen gradaties in mobielvriendelijkheid.

* Als je website met vlag en wimpel door de [Mobielvriendelijke test](https://www.google.com/webmasters/tools/mobile-friendly/) van Google komt, dan ziet Google ook per 21 april jouw site als mobielvriendelijk. Hetzelfde geldt als bij jouw website in mobiele zoekresultaten de grijze tekst “voor mobiel” staat vermeld.

Tot zover de extra nuances over de [mobielvriendelijke update van Google](https://www.youtube.com/watch?v=OznxHYA4QsQ).

## YouTube videomarketing nu met infokaarten en ook op mobiel!

![YouTube](/archive/reputatiecoaching/media/wp-content/uploads/2013/05/youtube-logo.png)

Alleen maar video’s op YouTube plaatsen in de hoop dat kijkers van je video’s de moeite nemen een URL die je in je video laat zien in te typen, is zinloos. Het is al beter als je in de beschrijving op YouTube je flink uitleeft en wat moeite doet om iets meer dan 1 regeltje tekst bij je video te typen. Vergeet niet: je hebt ruimte voor maar liefst zo’n 4.000 karakters in de beschrijving!

En wist je dat als je links in de beschrijving plaatst die je netjes laat beginnen met http://, dat deze dan als klikbare links worden omgezet? Zo kun je kijkers al iets gemakkelijker naar je website en andere bestemmingen op het wereldwijde web dirigeren.

Wat je daarna nog kunt doen om je video te gebruiken om mensen naar specifieke pagina’s op je website te leiden, of beter gezegd: ze kunt verleiden om naar je website te gaan, is gebruik te maken van de zogenaamde “aantekeningen”. Dat is het woord dat YouTube ervoor gebruikt in het Nederlands. In het Engels heet het “annotations”. Als je er eenmaal op hebt geklikt, dan zie je ook in de Nederlandse versie van YouTube de tekst “Annotatie toevoegen”.

Daarbij kun je kiezen uit verschillende mogelijkheden:

* Tekstballon

* Opmerking

* Titel

* Spotlight

* Label

Ongeacht welke je kiest: je kunt ze allemaal gebruiken om ergens naartoe te linken. Je kunt voor het linken kiezen uit:

* Video

* Afspeellijst

* Google+ profiel/-pagina

* Abonneren

* Project voor het inzamelen van geld

* Bijbehorende website

* Merchandise

Echter, ergens naartoe linken kan alleen als je je YouTube account ooit hebt geverifieerd. Als je ingelogd bent op YouTube, kun je surfen naar: [www.youtube.com/verify](https://www.youtube.com/verify) om je YouTube account te verifiëren. Dan krijg je het scherm te zien dat ik heb opgenomen in de show notes:

[![YouTube verfieer je account](https://lh5.googleusercontent.com/-ha6Gt9fZNow/VRP_TmpsWKI/AAAAAAAAB5c/cWcc73I3lUU/w967-h274-no/20150326-YTverify.png)

](https://lh5.googleusercontent.com/-ha6Gt9fZNow/VRP_TmpsWKI/AAAAAAAAB5c/cWcc73I3lUU/w967-h274-no/20150326-YTverify.png)

Daar moet je het land kiezen en de manier waarop je je account wilt verifiëren. Je kunt daar kiezen uit gebeld worden met een automatisch telefoontje, of via SMS. Ik maak je erop attent dat je per jaar hetzelfde nummer slechts drie keer kunt gebruiken. Maar voor de meeste mensen zal één keer zelfs wel voldoende zijn.

Als je de code hebt ingevoerd heb je opeens veel meer mogelijkheden in YouTube. Ook hiervan heb ik een screenshot opgenomen in de show notes, op [www.reputatiecoaching.nl/121](https://www.reputatiecoaching.nl/121/):

[![YouTube verified account](https://lh5.googleusercontent.com/-C1PtH6o6mZ8/VRQBwDU3ZwI/AAAAAAAAB6A/SqmjvdrlY2s/w773-h994-no/20150326-YTverified.png)

](https://lh5.googleusercontent.com/-C1PtH6o6mZ8/VRQBwDU3ZwI/AAAAAAAAB6A/SqmjvdrlY2s/w773-h994-no/20150326-YTverified.png)

Voor sommige mensen zal het prettig zijn dat ze nu inkomsten kunnen genereren met hun video’s, terwijl anderen blij zijn dat ze nu video’s kunnen uploaden die langer zijn dan 15 minuten. Zoals je in het overzicht van extra functies kunt zien heb je dan wel veel meer mogelijkheden, dus ik raad je zeker aan om je YouTube account te verifiëren op [www.youtube.com/verify](https://www.youtube.com/verify). Voorwaarde is geloof ik wel, dat je tenminste één video online moet hebben.

Maar sinds iets meer dan een week heeft YouTube er een nieuwe feature bij! Die feature heet: “Infokaarten”. In de show notes heb ik daar een voorbeeld van opgenomen, hoe dat eruit ziet:

[![YouTube infokaart voorbeeld](https://lh4.googleusercontent.com/-eoe15lkwH90/VRP_Tjty1tI/AAAAAAAAB5U/X33_y5QXkxQ/w852-h506-no/20150326-YT-infocard.png)

](https://lh4.googleusercontent.com/-eoe15lkwH90/VRP_Tjty1tI/AAAAAAAAB5U/X33_y5QXkxQ/w852-h506-no/20150326-YT-infocard.png)

Je kunt kiezen uit diverse soorten infokaarten, te weten:

* Bijbehorende website - om je website te promoten

* Geld inzamelen - om kijkers aan te moedigen bij te dragen aan je projecten op ondersteunde fondsenwervingsites

* Handelswaar - om een product onder de aandacht te brengen op verkoopsites

* Video of afspeellijst - voor het promoten van een video of afspeellijst

[![Voorbeelden van YouTube infokaarten](https://lh6.googleusercontent.com/-dYYqFDO6TAw/VRP_S53LEAI/AAAAAAAAB5g/bvb9d8UZxMk/w993-h616-no/20150326-YT-infocard-choice.png)

](https://lh6.googleusercontent.com/-dYYqFDO6TAw/VRP_S53LEAI/AAAAAAAAB5g/bvb9d8UZxMk/w993-h616-no/20150326-YT-infocard-choice.png)

Mogelijk werd je gelijk getriggerd toen ik het zojuist had over “handelswaar” en kreeg je meteen al visioenen om hoog scorende video’s te maken van je tweedehands Playmobil die je te koop aanbiedt op Marktplaats, of via affiliate links naar producten op Amazon.

Helaas, dat zal niet gaan. Want het aantal sites waar je naar kunt verwijzen is beperkt. Je kunt een actueel overzicht vinden op de [supportsite van Google](https://support.google.com/youtube/answer/2760471). De link er naartoe heb ik opgenomen onderaan de show notes van deze podcast, omdat ik ze hier niet allemaal wil opnoemen.

Wel wil ik er drie kort even uitlichten. En dat zijn:

* _iTunes_ – waarbij je kunt linken naar je app, ibook, muziek en zelfs naar je podcast!

* _Eventbrite_ – om vanuit video’s te linken naar events

* _Soundcloud_ – om te linken van een video naar muziek op Soundcloud

Zo heb ik al meteen even in mijn meest recente video een infokaart opgenomen met een link naar de podcast. En reken er maar op, dat ik dat ga doen in alle video’s!

Ik hoor je al vragen: “Maar hoezo heb ik infokaarten nodig, als ik al annotaties of aantekeningen heb?”. Dat infokaarten er mogelijk iets mooier uitzien dan de aantekeningen is niet het belangrijkste argument.

Nee, weet je wat het krachtigste is? Welnu, aantekeningen of annotaties werken alleen in YouTube-video’s die worden bekeken op een desktop. Maar…

**Infokaarten werken ook op mobiel!**Dus als je infokaarten gebruikt die ergens naartoe linken, dan werken die nu dus ook als mensen de video bekijken op een mobiele telefoon!

Laten we nu wat feiten uit de diverse podcasts van de afgelopen tijd bij elkaar schrapen en combineren:

1. Het mobiele zoekverkeer neemt toe en lijkt op korte termijn het zoekverkeer op desktops te overstijgen, als dat al niet gebeurd is, in een aantal landen

2. Video neemt almaar toe aan populariteit

3. YouTube is van Google en YouTube video’s kunnen goed scoren in de Google zoekresultaten

4. Binnenkort gaan mobielvriendelijke sites hoger scoren dan mobielonvriendelijke sites

5. Gebruikers die een video bekijken zijn 1,6x eerder bereid een product te kopen

6. We hebben nu infokaarten die werken in YouTube video’s die op mobiele apparaten worden bekeken!

Wow! Als je dit allemaal achter elkaar leest, dan snap je wel waarom ik er zo enthousiast over ben! Om dit onderwerp voor nu af te sluiten heb ik in de show notes een screenshot van de iPhone gemaakt, waarop je een infokaart kunt zien:

[![YouTube video op mobiel met infokaart](https://lh5.googleusercontent.com/-EHdgvIBhRQM/VRP_T_c5nfI/AAAAAAAAB5o/vW0J1um4oNw/w1334-h750-no/20150326-infokaart-mobiel.png)

](https://lh5.googleusercontent.com/-EHdgvIBhRQM/VRP_T_c5nfI/AAAAAAAAB5o/vW0J1um4oNw/w1334-h750-no/20150326-infokaart-mobiel.png)

En met deze beschouwing over infokaarten op YouTube kom ik dan weer aan het einde van deze [121e podcast](https://www.reputatiecoaching.nl/121/).

Als je de podcast leuk vindt en je wilt nog meer op de hoogte blijven, volg me dan op Twitter, via [@reputatiecoach1](https://twitter.com/reputatiecoach1).

Heb je inderdaad wat aan alle informatie die ik met je deel, help mij dan met het verder verbeteren en promoten van deze podcast. Abonneer je op de podcast, zodat je altijd meteen de nieuwste uitzending krijgt voorgeschoteld.

Zoek de podcast op, in [iTunes](https://www.reputatiecoaching.nl/itunes) of [Stitcher](https://www.reputatiecoaching.nl/stitcher), geef de podcast een sterrenbeoordeling en laat je reactie achter. Door de podcast te beoordelen op iTunes en/of Stitcher breng je de podcast onder de aandacht van een breder publiek.

Je kunt me verder helpen, door de podcast aan te bevelen bij vrienden of collega’s, waarvan je denkt dat ze er hun voordeel mee kunnen doen, of door ’m te delen op Twitter, like’n en delen op Facebook of een “+1” te geven op Google+.

En vergeet niet: ik ben hier om je te helpen! Als je een vraag of een probleem hebt met betrekking tot je online reputatie of de vindbaarheid van je website, kun je een mailtje sturen naar [podcast@reputatiecoaching.nl](mailto:podcast@reputatiecoaching.nl).

Als je dat te lastig vindt, of als je de podcast beluistert terwijl je in de auto zit en je hebt acuut een vraag, spreek dan een boodschap in op de ReputatieCoaching Hotline, op nummer: 084 - 883 15 56. Mogelijk behandel ik je vraag of probleem dan in een artikel of in de podcast.

En je kunt rechtstreeks op de website een voicemail achterlaten, door op de tab aan de rechterkant van elke pagina te klikken, en je bericht in te spreken. Dit was [ReputatieCoaching Podcast aflevering 121](https://www.reputatiecoaching.nl/121/) en mijn naam is [Eduard de Boer](http://nl.linkedin.com/in/eduarddeboer/nl).

Ik wens je de komende week weer succes met het werken aan je reputatie, zodat je meteen je reputatie voor jou kunt laten werken!

Tot volgende week!

Doei!

Links naar content die in deze podcast aan bod komt:

* [ReputatieCoaching Podcast in iTunes](https://www.reputatiecoaching.nl/itunes)

* [ReputatieCoaching Podcast op Stitcher](https://www.reputatiecoaching.nl/stitcher)

* [ReputatieCoaching Podcast op TuneIn Radio](http://tunein.com/radio/ReputatieCoaching-Podcast-p655084/)

* [ReputatieCoaching Podcast RSS-feed](https://feeds.reputatiecoaching.nl/ReputatieCoachingPodcast)

* [Google Webmaster Tools](https://www.google.com/webmasters/tools/)

* [Google Mobielvriendelijke test](https://www.google.com/webmasters/tools/mobile-friendly/)

* [Merchandising-annotaties](https://support.google.com/youtube/answer/2760471) in YouTube video’s
