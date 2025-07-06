from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    usos_url: str = "https://apps.usos.agh.edu.pl/services/tt/upcoming_ical?lang=pl&user_id={user_id}&key={key}"
    s3_bucket_name: str = "lectures-filter-bucket"


settings = Settings()
