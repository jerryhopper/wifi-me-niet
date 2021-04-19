# wifi-me-niet

Wifi-me-niet scanner &amp; submitter

De wifi-me-niet scanner is een wapen tegen het wifi-tracken in publieke ruimtes.


## wifi-me-niet client.

De wifi-me-niet client is een python script dat -met de juiste hardware- wifi beacons opvangt, en de mac-adressen verstuurt naar de wifi-me-niet website.

Meer over de [Wifi-me-niet Client](client/README.md)

## wifi-me-niet website

De wifi-me-niet website is het backend voor de wifi-me-niet client. Dit backend accepteert de mac-adressen van de client, en submit deze naar de wifi-tracking optout website van het MOA

Meer over de [Wifi-me-niet Server](server/README.md)


# Hoe werkt het?

Een apparaat met wifi, stuurt regelmatig Wifi signalen uit om te zien of er een netwerk is waar het mee kan verbinden.

Je mobiel verbindt thuis met jou thuis-wifi omdat jij dat heb ingesteld. Maar als je bij de supermarkt bent, dan is jou thuiswifi niet in bereik. Je telefoon stuurt continu signalen uit, om te zien of je in de buurt bent van je thuiswifi. 

Deze wifi bakens (beacons) bevatten je mac-adress - dat is een uniek serinummer van je wifi-netwerk adapter. De wifi-me-niet scanner vangt deze beacons op, en verstuurt deze naar de wifi-me-niet website waar het mac-adres weer word verstuurd naar de MOA optout pagina.


