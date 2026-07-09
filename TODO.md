# TODO - MySQL connection only (backend startup verification)

- [x] Update `backend/mysql_pool.py`
  - [x] Add `get_mysql_connection()` helper returning an active connection
  - [x] Ensure credentials are read from `.env` vars: MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
  - [x] On connection attempt, run `SELECT 1;` to verify
  - [x] Print required startup success/failure logs exactly as specified
- [ ] (If needed) Minimal log alignment in `backend/app.py`
- [ ] Run backend startup and confirm the log shows the required MySQL connection message
