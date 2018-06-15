CREATE USER tally_http_app WITH ENCRYPTED PASSWORD 'app'; -- NOTE: OBVIOUSLY this is for dev only.
CREATE USER tally_root WITH ENCRYPTED PASSWORD 'app';
GRANT tally_http_app TO tally_root;

CREATE DATABASE tallies;
REVOKE ALL ON DATABASE tallies FROM public;

-- NOTE: do not allow the app user to run migrations
GRANT CONNECT
ON DATABASE tallies
TO tally_http_app;

\connect tallies;

-- NOTE: I thought I could do all this from memory. I couldn't.
-- https://dba.stackexchange.com/questions/117109/how-to-manage-default-privileges-for-users-on-a-database-vs-schema
-- Erwin Brandstetter, if we ever meet. I'll buy you a beer

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO tally_http_app;
GRANT CREATE ON SCHEMA public TO tally_root;

ALTER DEFAULT PRIVILEGES
FOR ROLE tally_root -- when tally_root creates objects:
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO tally_http_app;

ALTER DEFAULT PRIVILEGES
FOR ROLE tally_root
GRANT USAGE, SELECT, UPDATE
ON SEQUENCES
TO tally_http_app;

ALTER DATABASE tallies OWNER TO tally_root;
