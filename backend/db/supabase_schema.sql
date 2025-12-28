-- Supabase Schema for The Third Voice AI
-- Run this in your Supabase SQL Editor to create the required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================
-- Users Table
-- ========================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_demo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ========================
-- Contacts Table
-- ========================
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for user's contacts
CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);

-- ========================
-- Messages Table
-- ========================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    contact_name VARCHAR(255),
    type VARCHAR(50) NOT NULL, -- 'transform', 'analyze', 'suggest'
    original TEXT NOT NULL,
    result TEXT NOT NULL,
    sentiment VARCHAR(50),
    emotional_state VARCHAR(100),
    model VARCHAR(100),
    healing_score INTEGER CHECK (healing_score >= 0 AND healing_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for message queries
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- ========================
-- AI Cache Table
-- ========================
CREATE TABLE IF NOT EXISTS ai_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message_hash VARCHAR(64) NOT NULL,
    context TEXT,
    response TEXT NOT NULL,
    model VARCHAR(100),
    healing_score INTEGER,
    sentiment VARCHAR(50),
    emotional_state VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index for cache lookups
CREATE INDEX IF NOT EXISTS idx_ai_cache_lookup ON ai_cache(message_hash, contact_id);
CREATE INDEX IF NOT EXISTS idx_ai_cache_expires ON ai_cache(expires_at);

-- ========================
-- Feedback Table
-- ========================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feature_context VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for feedback queries
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);

-- ========================
-- Demo Usage Table
-- ========================
CREATE TABLE IF NOT EXISTS demo_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255),
    ip_address VARCHAR(45),
    login_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for demo usage analytics
CREATE INDEX IF NOT EXISTS idx_demo_usage_login_time ON demo_usage(login_time DESC);

-- ========================
-- Row Level Security (RLS)
-- ========================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Users: Allow full access for service role (backend)
CREATE POLICY "Service role full access to users" ON users
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Contacts: Users can only access their own contacts
CREATE POLICY "Service role full access to contacts" ON contacts
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Messages: Users can only access their own messages
CREATE POLICY "Service role full access to messages" ON messages
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- AI Cache: Service role access
CREATE POLICY "Service role full access to ai_cache" ON ai_cache
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Feedback: Service role access
CREATE POLICY "Service role full access to feedback" ON feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Demo usage: No RLS needed (analytics only)

-- ========================
-- Updated At Trigger
-- ========================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================
-- Cleanup Function (optional)
-- ========================
-- Run this periodically to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ai_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ language 'plpgsql';
