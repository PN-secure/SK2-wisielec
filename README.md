# SK2-wisielec

## Opis projektu

**SK2-wisielec** to gra multiplayer typu "wisielec", która toczy się w czasie rzeczywistym. Gracze łączą się do wspólnej sesji gry i próbują odgadnąć wylosowane hasło, znajdujące się w zadanym pliku z hasłami.

### Zasady gry:

- Każda poprawnie odgadnięta litera daje graczowi dodatkową szansę na pomyłkę.
- Każda błędnie podana litera zmniejsza ilość dostępnych szans.
- Jeśli liczba szans gracza osiągnie 0, gracz przegrywa, ale dalej może obserwować rozgrywkę.
- Opuszczenie gry przez gracza nie przerywa rozgrywki – pozostali gracze są jedynie informowani o jego rozłączeniu.
- Wygrywa gracz, który jako pierwszy odgadnie swoje hasło.

## Uruchamianie serwera

Serwer wystarczy uruchomić tylko raz. Po zakończeniu każdej rozgrywki oczekuje na nowych graczy do kolejnej sesji.

Komenda uruchamiająca serwer:
```
server_app <port> <liczba_graczy> <plik_z_hasłami>
```
### Parametry:
- `<port>` – port, na którym nasłuchuje serwer (domyślnie: `8000`).
- `<liczba_graczy>` – wymagana liczba graczy do rozpoczęcia rozgrywki (domyślnie: `2`).
- `<plik_z_hasłami>` – plik z hasłami, przedzielonymi przecinkami (domyślnie: `words.txt`).

Możesz pominąć wszystkie parametry w komendzie; wtedy serwer uruchomi się z wartościami domyślnymi.

Przykłady:
1. **Domyślne wartości:**
    ```
    server_app
    ```
2. **Z podaniem parametrów:**
    ```
    server_app 9000 3 custom_words.txt
    ```

## Uruchamianie klienta

Po uruchomieniu klient zapyta o:
1. **Adres IP serwera.**
2. **Port serwera.**

Po połączeniu klient rozpoczyna oczekiwanie na dołączenie wcześniej określonej liczby graczy. Po spełnieniu tego warunku gra się rozpoczyna.

### Działanie klienta:

- Gracz zgaduje litery hasła, podając je za pomocą klawiatury.
- W trakcie gry gracz ma **podgląd na postępy innych uczestników**, w tym:
  - Liczbę pozostałych szans.
  - Postęp w zgadywanym haśle.
  - Odgadnięte litery.

Kto pierwszy odgadnie swoje hasło, ten wygrywa.
