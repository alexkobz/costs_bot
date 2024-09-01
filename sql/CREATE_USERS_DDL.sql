CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    is_bot BOOLEAN NOT NULL DEFAULT False,
    first_name VARCHAR(100) NOT NULL DEFAULT '',
    language_code VARCHAR(2) NOT NULL DEFAULT 'en',
    added_date TIMESTAMP,
    utc_offset INTEGER NOT NULL DEFAULT 0
)
;

INSERT INTO users (id, first_name, is_bot, language_code, added_date, utc_offset) VALUES (0, '', False, 'en', '1970-01-01 00:00:00', 0)
;

COMMIT;
