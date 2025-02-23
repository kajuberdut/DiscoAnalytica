# Database Table Types

## Table of Contents

- [1. Entity Tables](#1-entity-tables)
- [2. Lookup Tables](#2-lookup-tables)
- [3. Extended Data Tables](#3-extended-data-tables)
- [4. Feature Tables](#4-feature-tables)
- [5. Junction Tables](#5-junction-tables)
- [6. Other Table Types](#6-other-table-types)

## 1. Entity Tables

**Also known as:** Primary Tables, Core Tables

Entity tables store the main logical objects of the database. These objects represent real-world things or concepts, like songs, customers, or products.

**Example:**

- `tracks` table, which stores information about song tracks, such as their title, artist, and duration.

### Key Characteristics:

- Typically have a **primary key** (e.g., `track_id`)
- Contain **descriptive columns** (e.g., `title`, `duration`)
- Contain keys that point to lookup tables (e.g., "genre\_id")
- Serve as the **main subject** of the database

---

## 2. Lookup Tables

**Also known as:** Attribute Tables, Reference Tables, Dimension Tables (in data warehousing)

Lookup tables store predefined lists of values that other tables reference. These tables help maintain data consistency and reduce duplication.

**Example:**

- `genres` table, which stores a list of music genres, referenced by `tracks.genre_id`

### Key Characteristics:

- Typically contain an **ID column** (e.g., `genre_id`)
- Store a **small, finite set of values** (e.g., `Pop`, `Rock`, `Jazz`)
- Referenced by **foreign keys** in entity tables

---

## 3. Extended Data Tables

**Also known as:** Vertical Partition Tables, Auxiliary Tables

Extended data tables store additional, often large or optional, information about an entity. They reuse the entity’s primary key as their own to maintain a **one-to-one relationship**.

**Example:**

- `lyrics` table, which stores song lyrics and references `tracks.track_id`

### Key Characteristics:

- **Primary key is also a foreign key** to the entity table
- Used to store **large text fields, images, or rarely used attributes**
- Helps **optimize performance** by separating less frequently queried data

---

## 4. Feature Tables

**Also known as:** Analytical Tables, Fact Tables (in data warehousing)

Feature tables store multiple numerical or categorical attributes about an entity, often used for analysis or machine learning.

**Example:**

- `track_features` table, which contains attributes like `danceability`, `tempo`, and `energy` for each track.

### Key Characteristics:

- Primary key is **typically a foreign key** to an entity table
- Contains multiple **measurable attributes** (e.g., float values for music characteristics)
- Used for **data analysis, reporting, or machine learning**

---

## 5. Junction Tables

**Also known as:** Linking Tables, Association Tables, Bridge Tables, Join Tables

Junction tables manage **many-to-many relationships** by storing references to two or more entity tables.

**Example:**

- `track_artists` table, which links tracks to multiple artists.

### Key Characteristics:

- Contains **only foreign keys** pointing to other tables
- Primary key is **often a composite key** (combining two foreign keys)
- Helps efficiently manage **complex relationships**

---

## 6. Other Table Types

### Log Tables

Used for **tracking changes** or recording events, such as user activity or modifications to data.

**Example:** `track_changes` table logs updates to track information.

### Staging Tables

Temporary tables used in **ETL (Extract, Transform, Load) processes** to hold intermediate data before it is loaded into the main database.

**Example:** `staging_tracks` table stores incoming track data before validation.

### Archive Tables

Store **old or infrequently used data** to keep the main database optimized.

**Example:** `archived_tracks` stores deleted or historical track records.

---

This guide provides an overview of key table types in databases. Understanding these structures can help you design efficient and well-organized databases!

