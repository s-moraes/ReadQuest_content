# Hybrid Data Models: JSONB & PostGIS

One of PostgreSQL's most distinctive capabilities is its ability to combine strict relational schemas with flexible semi-structured documents and specialized domains inside the same database engine.

---

## `JSON` vs `JSONB`: The Modern Document Store

PostgreSQL provides two data types for handling JSON:

| Feature | `JSON` | `JSONB` (Recommended) |
| :--- | :--- | :--- |
| **Storage Format** | Plain text (exact verbatim copy, including whitespace) | Decomposed binary format |
| **Ingestion Speed** | Faster (no parsing overhead) | Slightly slower (must be parsed into binary) |
| **Query & Retrieval** | Slower (re-parsed on every access) | Substantially faster (direct binary traversal) |
| **Key Ordering** | Preserved | Reordered for optimal retrieval |
| **Duplicate Keys** | Preserved | Last key wins |
| **Indexing** | Limited (expression indexes only) | Fully indexable with GIN indexes |

```sql
CREATE TABLE product_catalog (
    sku         TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    attributes  JSONB NOT NULL
);

-- Insert arbitrary nested semi-structured attributes
INSERT INTO product_catalog (sku, title, attributes) VALUES
('LAPTOP-X1', 'Pro Laptop 16', '{
    "specs": {"cpu": "M3 Max", "ram_gb": 64, "storage_tb": 2},
    "tags": ["developer", "portable", "high-end"],
    "warranty_years": 3
}');
```

### Essential JSONB Operators:
- `attributes -> 'specs'` : Returns JSON object for key.
- `attributes ->> 'title'` : Returns text value.
- `attributes #> '{specs, cpu}'` : Extracts nested element at path.
- `attributes @> '{"tags": ["developer"]}'` : **Containment test** (checks if left JSONB contains right JSONB).

```sql
-- Create a Generalized Inverted Index (GIN) for instant sub-millisecond document search
CREATE INDEX idx_products_attr_gin ON product_catalog USING GIN (attributes);

-- High-speed containment query using the GIN index
SELECT title FROM product_catalog 
WHERE attributes @> '{"specs": {"ram_gb": 64}}';
```

---

## Geospatial Power with PostGIS

PostGIS is an open-source extension that transforms PostgreSQL into a spatial database conforming to OpenGIS specifications. It powers major mapping, logistics, rideshare, and telemetry platforms worldwide.

```sql
-- Enable PostGIS in your database
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE delivery_vehicles (
    vehicle_id  INT PRIMARY KEY,
    driver_name TEXT NOT NULL,
    current_pos GEOMETRY(Point, 4326) -- WGS 84 coordinate reference system
);

-- Insert geospatial coordinates (Longitude, Latitude)
INSERT INTO delivery_vehicles VALUES 
(101, 'Alice', ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326));

-- Spatial GiST index for real-time spatial queries
CREATE INDEX idx_vehicle_pos_gist ON delivery_vehicles USING GIST (current_pos);

-- Find all vehicles within a 5 km radius of a warehouse point
SELECT vehicle_id, driver_name, 
       ST_Distance(current_pos::geography, ST_MakePoint(-122.4000, 37.7800)::geography) AS distance_meters
FROM delivery_vehicles
WHERE ST_DWithin(
    current_pos::geography, 
    ST_MakePoint(-122.4000, 37.7800)::geography, 
    5000
);
```

---

## Native Arrays and `hstore`

### 1. Native Arrays
PostgreSQL natively supports multidimensional arrays of any data type:

```sql
CREATE TABLE blog_posts (
    post_id   SERIAL PRIMARY KEY,
    title     TEXT NOT NULL,
    tags      TEXT[] NOT NULL -- Array of strings
);

-- Find posts tagged with both 'postgres' and 'architecture'
SELECT * FROM blog_posts 
WHERE tags @> ARRAY['postgres', 'architecture'];

-- Unnest array elements into individual relational rows
SELECT post_id, UNNEST(tags) AS individual_tag FROM blog_posts;
```

### 2. `hstore` Key-Value Store
Before `JSONB` became the industry standard, PostgreSQL introduced the `hstore` module to store sets of key/value pairs within a single PostgreSQL data field:

```sql
CREATE EXTENSION IF NOT EXISTS hstore;

CREATE TABLE user_settings (
    user_id     INT PRIMARY KEY,
    preferences HSTORE
);

INSERT INTO user_settings VALUES 
(1, 'theme => dark, notifications => enabled, font_size => 14');

SELECT preferences -> 'theme' FROM user_settings WHERE user_id = 1;
```

---

## Built-In Full-Text Search (FTS)

Without deploying an external search cluster, PostgreSQL provides linguistically aware full-text search:

```sql
-- tsvector: Parsed document representation of lexemes
-- tsquery: Search query expression with boolean operators (&, |, !)
SELECT title 
FROM product_catalog
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'laptop & portable');
```
