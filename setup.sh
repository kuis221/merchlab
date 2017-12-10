export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql://localhost/merch_db"
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
redis-server &