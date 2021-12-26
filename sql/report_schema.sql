BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER,
	"is_group"	INTEGER NOT NULL CHECK("is_group" = 0 OR "is_group" = 1),
	"name"	TEXT NOT NULL,
	"screen_name"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "post" (
	"id"	INTEGER,
	"user_id"	INTEGER NOT NULL,
	"time"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "hash_tag" (
	"post_hash_id"	INTEGER,
	"post_id"	INTEGER NOT NULL,
	"tag"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	PRIMARY KEY("post_hash_id" AUTOINCREMENT)
);
COMMIT;
