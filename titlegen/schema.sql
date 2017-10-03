create table if not exists votes (
    id serial primary key,
    title varchar not null,
    is_cool boolean not null,
    insert_timestamp timestamp not null
)
