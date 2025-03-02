-- Create table_type table to categorize different types of tables
CREATE TABLE IF NOT EXISTS table_type (
      type_id INTEGER PRIMARY KEY
    , name TEXT NOT NULL
);

-- Insert predefined table types
INSERT OR IGNORE INTO table_type (type_id, name) VALUES
      (1, 'Entity Tables')
    , (2, 'Lookup Tables')
    , (3, 'Extended Data Tables')
    , (4, 'Feature Tables')
    , (5, 'Junction Tables')
    , (6, 'Log Tables')
    , (7, 'Staging Tables')
    , (8, 'Archive Tables')
;

-- Create data_provider table to store data providers
CREATE TABLE IF NOT EXISTS data_provider (
      provider_id INTEGER PRIMARY KEY
    , name TEXT NOT NULL UNIQUE
);

-- Insert predefined data providers
INSERT OR IGNORE INTO provider (provider_id, name) VALUES
    (1, 'Kaggle')
;

-- Create source_type table to store file types
CREATE TABLE IF NOT EXISTS data_file_type (
      file_type_id INTEGER PRIMARY KEY
    , name TEXT NOT NULL UNIQUE
);

-- Insert predefined source types
INSERT OR IGNORE INTO data_file_type (file_type_id, name) VALUES
      (1, 'CSV')
    , (2, 'Parquet')
    , (3, 'JSON')
;

-- Create data_definitions table to track external data sources
CREATE SEQUENCE IF NOT EXISTS seq_data_definition_id START 1;
 
CREATE TABLE IF NOT EXISTS data_definitions (
      data_definition_id INTEGER PRIMARY KEY DEFAULT nextval('seq_data_definition_id')
    , name TEXT NOT NULL
    , external_id TEXT NOT NULL
    , provider_id INTEGER NOT NULL
    , url TEXT NOT NULL
    , file_type_id INTEGER NOT NULL
    , license TEXT NOT NULL
    , attribution TEXT NOT NULL
    , hash TEXT NOT NULL UNIQUE
    , filename TEXT NOT NULL
    , FOREIGN KEY (provider_id) REFERENCES data_provider(provider_id)
    , FOREIGN KEY (file_type_id) REFERENCES data_file_type(file_type_id)
);

-- Create table_info table to store metadata about tables
CREATE SEQUENCE IF NOT EXISTS seq_table_info_id START 1;

CREATE TABLE IF NOT EXISTS table_info (
      table_info_id INTEGER PRIMARY KEY DEFAULT nextval('seq_table_info_id')
    , table_name TEXT UNIQUE
    , type_id INTEGER NOT NULL
    , description TEXT
    , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , FOREIGN KEY (type_id) REFERENCES table_type(type_id)
);


-- Create a log table for data loads
CREATE SEQUENCE seq_data_log_id START 1;

CREATE TABLE data_log (
      data_log_id INTEGER PRIMARY KEY DEFAULT nextval('seq_data_log_id')
    , data_load_session_id UUID
    , table_info_id INTEGER REFERENCES table_info(table_info_id)
    , data_definition_id INTEGER REFERENCES data_definitions(data_definition_id)
    , load_start_time TIMESTAMP_MS
    , load_end_time TIMESTAMP_MS
    , rows_affected INTEGER
);

