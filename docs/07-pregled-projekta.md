# Pregled projekta

Pregledal sem dokumentacijo (`docs/01`–`06`), ADR-je in kodo ter aplikacijo zagnal lokalno (Docker Compose, lastna Supabase baza in Firebase projekt). Funkcionalnosti sem preizkusil ročno.

## Implementirane funkcionalnosti MVP

| Funkcionalnost | Zgodba | Stanje |
| --- | --- | --- |
| Iskanje knjig (katalog, Open Library, ISBN) | US-01 | Implementirano |
| Uvoz iz Goodreadsa | US-02 | Delno |
| Dodajanje knjige v knjižnico | US-04 | Implementirano |
| Filtriranje in razvrščanje knjižnice | US-05 | Implementirano |
| Evidenca posoj | US-06 | Implementirano |
| Status branja | US-07 | Implementirano |
| Ocena in recenzija | US-08 | Ni implementirano |
| Letni bralni cilj | US-10 | Implementirano |

Implementirani sta tudi registracija in prijava (Firebase Authentication).

**Kaj manjka:**

- US-08: Oceni in recenziji sta v bazi predvideni, v aplikaciji pa ju ni mogoče vnesti.
- US-02: Uvoz prenese statuse branja in datume branja, pred uvozom pa prikaže predogled (število knjig po statusih in knjige brez ISBN). Ocene in recenzije se ne uvozijo. Po uvozu se prikaže samo "Import finished", brez povzetka uvoženih, obstoječih in neprepoznanih knjig.
Aplikacija shranjuje samo knjige z ISBN, zato starejših knjig brez ISBN ni mogoče najti. Uporabniški vmesnik je v angleščini.

## Ujemanje z uporabniškimi zgodbami

**US-01 – Iskanje knjig**
Iskanje se sproži pri vsaj 4 znakih. Najprej se prikažejo zadetki iz kataloga, nato se dopolnijo iz Open Library. Zadetki imajo naslovnico, naslov, avtorja in serijo. Iskanje po ISBN vrne točno to izdajo, brez zadetkov se prikaže "No results".

**US-04 – Dodajanje v knjižnico**
Uporabnik izbere izdajo (naslovnica, založba, leto, format) ter po želji vpiše lokacijo in opombe. Ponovno dodajanje iste izdaje zahteva potrditev. Knjiga se prikaže v knjižnici z oznako formata.

**US-05 – Filtriranje in razvrščanje**
Filtri (format, žanr, zbirka, serija, prebrano/neprebrano) se kombinirajo. Razvrščati je mogoče po naslovu in avtorju v obe smeri. Prikazano je število knjig, "Clear filters" pa vse ponastavi.

**US-06 – Evidenca posoj**
Posoja shrani ime in datum (privzeto danes), knjiga dobi oznako "Lent to". Ponovna posoja ni mogoča, dokler knjiga ni vrnjena. Vrnjene posoje ostanejo v zgodovini, vidi jih samo lastnik.

**US-07 – Status branja**
Knjiga ima en status, tudi če je ni v knjižnici. Datum začetka in konca se shranita samodejno in ju je mogoče spremeniti, datuma v prihodnosti pa ni mogoče izbrati. Knjiga, prebrana brez datuma, se ne šteje v letni cilj.

## Povzetek

Vseh pet pregledanih zgodb je izpolnjenih. Robne primere (ponovno dodajanje, ponovna posoja, datum v prihodnosti) prepreči že uporabniški vmesnik, backend pa jih preveri še enkrat. Od MVP manjkata ocena in recenzija (US-08) ter del uvoza iz Goodreadsa (US-02).