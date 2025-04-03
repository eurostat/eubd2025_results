Aby zrobić portable bazę danych użyjemy pg_dump:

W kontenerze:

``` docker exec -t postgres pg_dump -U shiny_user shiny_db > shiny_db.dump ```

Ten dump będzie trzeba trzymać w jakiejś bezpiecznej lokalizacji, dzięki temu mamy mniej więcej przenośneDB, oraz backup w razie jakby coś poszło nie tak.

Aby odtworzyć bazę danych na nowym systemie, lub jakby coś się stało z naszym db na oryginalnym systemie,użyjemy pg_restore w kontenerze postgres'a:

``` cat shiny_db.dump | docker exec -i postgres psql -U shiny_user -d shiny_db ```

W przypadku robienia dumpa np. Z serwer'a Jupyter:

``` pg_dump -U shiny_user -h 127.0.0.1 -d shiny_db -F c -f shiny_db.dump ```

Potem przenieś plik shiny_db.dump na serwer/komputer aplikacyjny i wykonaj komendę 2.
