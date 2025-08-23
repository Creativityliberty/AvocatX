-- Script d'initialisation PostgreSQL pour DEFENSEUR-IA

-- Création de la base de données et des utilisateurs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table principale des dossiers
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    dossier_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    data JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    type_contentieux VARCHAR(100),
    client_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_cases_dossier_id ON cases(dossier_id);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_type ON cases(type_contentieux);
CREATE INDEX IF NOT EXISTS idx_cases_created ON cases(created_at);
CREATE INDEX IF NOT EXISTS idx_cases_data ON cases USING GIN(data);

-- Table des clients
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    client_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    telephone VARCHAR(50),
    date_naissance DATE,
    adresse TEXT,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index clients
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_clients_nom ON clients(nom);
CREATE INDEX IF NOT EXISTS idx_clients_data ON clients USING GIN(data);

-- Table des documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    dossier_id UUID REFERENCES cases(dossier_id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    type_document VARCHAR(50),
    description TEXT,
    data JSONB NOT NULL DEFAULT '{}',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_status VARCHAR(50) DEFAULT 'pending'
);

-- Index documents
CREATE INDEX IF NOT EXISTS idx_documents_dossier ON documents(dossier_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type_document);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded ON documents(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_documents_data ON documents USING GIN(data);

-- Table des rendez-vous
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    appointment_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(client_id),
    dossier_id UUID REFERENCES cases(dossier_id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'scheduled',
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index appointments
CREATE INDEX IF NOT EXISTS idx_appointments_client ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_dossier ON appointments(dossier_id);
CREATE INDEX IF NOT EXISTS idx_appointments_start ON appointments(start_time);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_data ON appointments USING GIN(data);

-- Table des statuts de pipeline
CREATE TABLE IF NOT EXISTS pipeline_status (
    id SERIAL PRIMARY KEY,
    dossier_id UUID REFERENCES cases(dossier_id),
    current_step INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pipeline_status
CREATE INDEX IF NOT EXISTS idx_pipeline_dossier ON pipeline_status(dossier_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_status ON pipeline_status(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_updated ON pipeline_status(updated_at);
CREATE INDEX IF NOT EXISTS idx_pipeline_data ON pipeline_status USING GIN(data);

-- Table des logs du pipeline
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    dossier_id UUID REFERENCES cases(dossier_id),
    step_number INTEGER NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    log_level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pipeline_logs
CREATE INDEX IF NOT EXISTS idx_logs_dossier ON pipeline_logs(dossier_id);
CREATE INDEX IF NOT EXISTS idx_logs_step ON pipeline_logs(step_number);
CREATE INDEX IF NOT EXISTS idx_logs_agent ON pipeline_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_logs_created ON pipeline_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_data ON pipeline_logs USING GIN(data);

-- Fonctions de mise à jour automatique
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mise à jour automatique
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_status_updated_at BEFORE UPDATE ON pipeline_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour les statistiques
CREATE OR REPLACE VIEW stats_overview AS
SELECT 
    (SELECT COUNT(*) FROM cases) as total_cases,
    (SELECT COUNT(*) FROM cases WHERE data->>'status' = 'completed') as completed_cases,
    (SELECT COUNT(*) FROM cases WHERE data->>'status' = 'processing') as processing_cases,
    (SELECT COUNT(*) FROM cases WHERE data->>'status' = 'error') as error_cases,
    (SELECT COUNT(*) FROM clients) as total_clients,
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM appointments) as total_appointments,
    (SELECT COUNT(*) FROM documents WHERE processing_status = 'completed') as processed_documents,
    (SELECT COUNT(*) FROM documents WHERE processing_status = 'pending') as pending_documents;

-- Insertion de données de test
INSERT INTO clients (nom, prenom, email, data) VALUES
('Dupont', 'Jean', 'jean.dupont@example.com', '{"type_contentieux": "OQTF", "situation": "urgente"}'),
('Martin', 'Marie', 'marie.martin@example.com', '{"type_contentieux": "titre_sejour", "situation": "renouvellement"}'),
('Bernard', 'Pierre', 'pierre.bernard@example.com', '{"type_contentieux": "naturalisation", "situation": "demande"}');

-- Données de test pour les dossiers
INSERT INTO cases (dossier_id, data, status, type_contentieux) VALUES
('550e8400-e29b-41d4-a716-446655440001', '{"title": "OQTF - Jean Dupont", "description": "Recours contre OQTF", "client": "jean.dupont@example.com"}', 'pending', 'OQTF'),
('550e8400-e29b-41d4-a716-446655440002', '{"title": "Titre Séjour - Marie Martin", "description": "Renouvellement titre séjour", "client": "marie.martin@example.com"}', 'processing', 'titre_sejour'),
('550e8400-e29b-41d4-a716-446655440003', '{"title": "Naturalisation - Pierre Bernard", "description": "Demande de naturalisation", "client": "pierre.bernard@example.com"}', 'completed', 'naturalisation');
