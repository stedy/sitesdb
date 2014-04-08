library(RSQLite)
conn <- dbConnect(SQLite(), dbname="mb.db")
raw.events <- dbGetQuery(conn, "SELECT * FROM events")
raw.events$row_names <- NULL
raw.events$sql_date <- as.Date(raw.events$eventdate, "%m/%d/%Y")
raw.events$sql_date <- as.character(raw.events$sql_date)
raw.events[is.na(raw.events)] <- ""
dbSendQuery(conn, "DROP TABLE IF EXISTS events")
dbWriteTable(conn, "events", raw.events)

dbDisconnect(conn)
