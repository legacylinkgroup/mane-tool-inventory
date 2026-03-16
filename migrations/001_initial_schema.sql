-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Create boxes table
CREATE TABLE boxes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(100) NOT NULL,
    sublocation VARCHAR(100),
    qr_code_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create items table
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    box_id UUID NOT NULL REFERENCES boxes(id) ON DELETE CASCADE,
    dropbox_manual_url TEXT,
    image_url TEXT,
    brand_platform VARCHAR(100),
    serial_number VARCHAR(100),
    estimated_value DECIMAL(10,2),
    low_stock_threshold INTEGER DEFAULT 5,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (name, box_id) -- Composite unique constraint for merge strategy
);

-- Create indexes for performance
CREATE INDEX idx_boxes_location ON boxes(location);
CREATE INDEX idx_boxes_name ON boxes(name);

CREATE INDEX idx_items_box_id ON items(box_id);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_name_trgm ON items USING GIN (name gin_trgm_ops); -- Fuzzy search

-- Create trigger to auto-update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_items_last_updated
BEFORE UPDATE ON items
FOR EACH ROW
WHEN (OLD.quantity IS DISTINCT FROM NEW.quantity OR
      OLD.name IS DISTINCT FROM NEW.name OR
      OLD.category IS DISTINCT FROM NEW.category)
EXECUTE FUNCTION update_last_updated();

-- Create trigger to auto-update boxes updated_at
CREATE TRIGGER trigger_update_boxes_updated_at
BEFORE UPDATE ON boxes
FOR EACH ROW
EXECUTE FUNCTION update_last_updated();

-- Create Supabase Storage buckets (run in Supabase SQL Editor or via API)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('tool-images', 'tool-images', true);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('qr-codes', 'qr-codes', true);

-- Disable Row-Level Security for single-user mode (run in Supabase SQL Editor)
-- ALTER TABLE boxes DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE items DISABLE ROW LEVEL SECURITY;
