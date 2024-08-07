DROP TABLE IF EXISTS "genre_aux";
DROP TABLE IF EXISTS "genre";
DROP TABLE IF EXISTS "favourite";
DROP TABLE IF EXISTS "review";
DROP TABLE IF EXISTS "comment";
DROP TABLE IF EXISTS "chapter";
DROP INDEX IF EXISTS "novel_fts";
DROP TABLE IF EXISTS "novel";
DROP TABLE IF EXISTS "user";
DROP TYPE IF EXISTS "rights";
DROP TYPE IF EXISTS "genre_type";

CREATE TYPE "rights" AS
ENUM ('admin_','user_');

CREATE TYPE "genre_type" AS
ENUM ('genre_', 'tag_');

CREATE TABLE "user" (
	id serial NOT NULL,
	rights rights NOT NULL DEFAULT 'user_',
	nickname varchar(100) NOT NULL,
	password CHAR(60) NOT NULL,
	reg_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	e_mail varchar(40) NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (id),
	CONSTRAINT user_nickname_uq UNIQUE (nickname),
	CONSTRAINT user_e_mail_uq UNIQUE (e_mail)
);

CREATE TABLE "novel" (
	id serial NOT NULL,
	name varchar(200) NOT NULL,
	description text,
	rating real NOT NULL DEFAULT 0,
	votes integer NOT NULL DEFAULT 0,
	id_user integer NOT NULL,
	CONSTRAINT novel_pk PRIMARY KEY (id),
  CONSTRAINT user_fk FOREIGN KEY (id_user)
    REFERENCES "user" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX "novel_fts" ON "novel" USING GIN (to_tsvector('english', name));

CREATE TABLE "chapter" (
	id serial NOT NULL,
	order_num integer NOT NULL,
	text text NOT NULL,
	id_novel integer NOT NULL,
	CONSTRAINT chapter_pk PRIMARY KEY (id),
  CONSTRAINT novel_fk FOREIGN KEY (id_novel)
    REFERENCES "novel" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chapter_id_novel_order_num_uq UNIQUE (id_novel, order_num),
  CONSTRAINT chapter_order_num_ck CHECK (order_num > 0)
);

CREATE TABLE "comment" (
	id serial NOT NULL,
	text varchar(1000) NOT NULL,
	id_chapter integer NOT NULL,
	id_user integer NOT NULL,
	CONSTRAINT comment_pk PRIMARY KEY (id),
  CONSTRAINT chapter_fk FOREIGN KEY (id_chapter)
    REFERENCES "chapter" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT user_fk FOREIGN KEY (id_user)
    REFERENCES "user" (id) MATCH FULL
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE "review" (
	id serial NOT NULL,
	rating integer NOT NULL,
	text text,
	id_novel integer NOT NULL,
	id_user integer NOT NULL,
	CONSTRAINT review_pk PRIMARY KEY (id),
  CONSTRAINT novel_fk FOREIGN KEY (id_novel)
    REFERENCES "novel" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT user_fk FOREIGN KEY (id_user)
    REFERENCES "user" (id) MATCH FULL
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT review_uq UNIQUE (id_novel, id_user),
	CONSTRAINT review_rating_ck CHECK (rating >= 1 AND rating <= 5)
);

CREATE TABLE "favourite" (
	id_novel integer NOT NULL,
	hide bool NOT NULL DEFAULT FALSE,
	id_user integer NOT NULL,
	CONSTRAINT favourite_pk PRIMARY KEY (id_novel, id_user),
  CONSTRAINT user_fk FOREIGN KEY (id_user)
    REFERENCES "user" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "genre" (
	id serial NOT NULL,
	genre varchar(60) NOT NULL,
	genre_type genre_type NOT NULL DEFAULT 'tag_',
	CONSTRAINT genre_pk PRIMARY KEY (id),
	CONSTRAINT genre_uq UNIQUE (genre)
);

CREATE TABLE "genre_aux" (
	id_genre integer NOT NULL,
	id_novel integer NOT NULL,
	CONSTRAINT genre_aux_pk PRIMARY KEY (id_genre,id_novel),
  CONSTRAINT genre_fk FOREIGN KEY (id_genre)
    REFERENCES "genre" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT novel_fk FOREIGN KEY (id_novel)
    REFERENCES "novel" (id) MATCH FULL
    ON DELETE CASCADE ON UPDATE CASCADE
);
