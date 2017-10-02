create table if not exists votes (
    id integer primary key autoincrement,
    title text not null,
    is_cool boolean not null,
    insert_timestamp timestamp not null
)
