-- Fix boxes table trigger to update 'updated_at' instead of 'last_updated'

-- Drop the existing incorrect trigger
DROP TRIGGER IF EXISTS trigger_update_boxes_updated_at ON boxes;

-- Create proper function for boxes updated_at
CREATE OR REPLACE FUNCTION update_boxes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create corrected trigger for boxes
CREATE TRIGGER trigger_update_boxes_updated_at
BEFORE UPDATE ON boxes
FOR EACH ROW
EXECUTE FUNCTION update_boxes_updated_at();

-- Create Supabase Storage buckets with public access
-- INSERT INTO storage.buckets (id, name, public) VALUES ('tool-images', 'tool-images', true) ON CONFLICT DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('qr-codes', 'qr-codes', true) ON CONFLICT DO NOTHING;

-- Disable Row-Level Security on storage buckets (run manually in Supabase dashboard)
-- Storage > Settings > Policies > Disable RLS for both buckets
