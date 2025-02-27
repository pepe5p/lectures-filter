# lectures-filter

AWS Lambda code that fetches .ics calendar and removes all lectures from it :).

1. Build docker image:
    ```
    docker compose build lectures-filter
    ```

2. Run docker container:
    ```
    docker compose lectures-filter run bash
    ```
    or with make
    ```
    make dc_bash
    ```

3. Run tests:
    ```
    make test
    ```
