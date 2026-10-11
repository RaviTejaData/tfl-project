import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

create_sql = """
CREATE TABLE IF NOT EXISTS line_status (
    fetched_at    timestamptz NOT NULL,
    line_id       text        NOT NULL,
    status_index  integer     NOT NULL,
    line_name     text        NOT NULL,
    severity      integer     NOT NULL,
    status        text        NOT NULL,
    reason        text,
    PRIMARY KEY (fetched_at, line_id, status_index)
);

ALTER TABLE line_status ENABLE ROW LEVEL SECURITY;


CREATE TABLE IF NOT EXISTS reason_classification (
    reason                      text PRIMARY KEY,
    cause_category              text        NOT NULL,
    is_planned                  boolean     NOT NULL,
    cause_location              text,
    affected_section            text,
    tickets_accepted_elsewhere  boolean     NOT NULL,
    model                       text        NOT NULL,
    classified_at               timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE reason_classification ENABLE ROW LEVEL SECURITY;

"""

with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
    conn.execute(create_sql)

print("Tables are ready")
