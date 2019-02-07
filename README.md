# Analiza współautorstwa

## Treść zadania
Na [stronie](https://apacz.matinf.uj.edu.pl/jednostki/1-wydzial-matematyki-i-informatyki-uj) znajdują się publikacje pracowników wydziału - proszę przygotować analizę współautorstwa z ciekawą warstwą prezentacji (grafowa + interaktywna)

## Opis projektu

### Przygotowanie danych

Dane zostały wstępnie pobrane w postaci plików XHTML zawierających publikacje opublikowane w poszczególnych latach oraz informacji o autorach. Schemat katalogów jest następujący:

- wmii_pages
    - authors - informacje o autorach
    - papers - publikacje wydane w poszczególnych latach

Następnie zebrano następujące dane:

- imię
- nazwisko
- url do strony autora
- artykuły, których dana osoba jest autorem
- jednoski w których pracuje dana osoba

### Prezentacja danych
Dane przedstawiono w postacii grafu, gdzie wierzchołkami są autorzy, a krawędziami współautorstwo. Dodatkowo grubość krawędzi zależy od liczby wspólnych publikacji, kolor wierzchołka od liczby opublikowanych artykułów, jego wielkość od liczby połączeń z innymi autorami.



