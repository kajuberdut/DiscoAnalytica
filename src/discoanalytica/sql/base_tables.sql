CREATE TABLE table_type (
    type_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT OR IGNORE INTO table_type (type_id, name) VALUES
    (1, 'Entity Tables'),
    (2, 'Lookup Tables'),
    (3, 'Extended Data Tables'),
    (4, 'Feature Tables'),
    (5, 'Junction Tables'),
    (6, 'Log Tables'),
    (7, 'Staging Tables'),
    (8, 'Archive Tables')
;
